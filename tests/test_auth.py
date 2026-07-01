"""Tests for shared_models.auth — User models + JWTAuthManager (TDD RED→GREEN)"""
import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt
from shared_models.auth import (
    JWTAuthManager,
    JWTPayload,
    UserLoginRequest,
    UserRegisterRequest,
    UserProfile,
    UserResponse,
    TokenResponse,
    RefreshRequest,
)


class TestUserLoginRequest:
    """UserLoginRequest validation"""

    def test_valid_login(self):
        req = UserLoginRequest(account="testuser", password="secret123")
        assert req.account == "testuser"
        assert req.password == "secret123"
        assert req.login_method == "password"

    def test_empty_account_raises(self):
        with pytest.raises(Exception):
            UserLoginRequest(account="", password="secret123")

    def test_empty_password_raises(self):
        with pytest.raises(Exception):
            UserLoginRequest(account="testuser", password="")

    def test_sms_login_method(self):
        req = UserLoginRequest(account="13800138000", password="123456", login_method="sms")
        assert req.login_method == "sms"

    def test_invalid_login_method_raises(self):
        with pytest.raises(Exception):
            UserLoginRequest(account="testuser", password="secret123", login_method="wechat")


class TestUserRegisterRequest:
    """UserRegisterRequest validation"""

    def test_valid_register(self):
        req = UserRegisterRequest(username="newuser", password="securepass123")
        assert req.username == "newuser"
        assert req.password == "securepass123"

    def test_username_too_short_raises(self):
        with pytest.raises(Exception):
            UserRegisterRequest(username="ab", password="securepass123")

    def test_password_too_short_raises(self):
        with pytest.raises(Exception):
            UserRegisterRequest(username="validuser", password="short")

    def test_with_email(self):
        req = UserRegisterRequest(username="user1", password="pass12345", email="user@example.com")
        assert req.email == "user@example.com"

    def test_verify_code_optional(self):
        req = UserRegisterRequest(username="user1", password="pass12345")
        assert req.verify_code is None


class TestTokenResponse:
    """TokenResponse model"""

    def test_minimal(self):
        resp = TokenResponse(access_token="abc123")
        assert resp.access_token == "abc123"
        assert resp.token_type == "bearer"
        assert resp.expires_in == 7200
        assert resp.role == "user"

    def test_with_refresh_token(self):
        resp = TokenResponse(access_token="abc", refresh_token="xyz")
        assert resp.refresh_token == "xyz"

    def test_full(self):
        resp = TokenResponse(
            access_token="abc",
            refresh_token="xyz",
            token_type="Bearer",
            expires_in=3600,
            user_id=42,
            username="tester",
            role="admin",
        )
        assert resp.user_id == 42
        assert resp.username == "tester"
        assert resp.role == "admin"
        assert resp.expires_in == 3600

    def test_expires_in_positive(self):
        resp = TokenResponse(access_token="abc", expires_in=0)
        assert resp.expires_in == 0


class TestRefreshRequest:
    """RefreshRequest model"""

    def test_valid(self):
        req = RefreshRequest(refresh_token="rtoken123")
        assert req.refresh_token == "rtoken123"


class TestUserResponse:
    """UserResponse model"""

    def test_minimal(self):
        resp = UserResponse(id="uuid-1", username="tester", email="test@example.com")
        assert resp.id == "uuid-1"
        assert resp.username == "tester"
        assert resp.email == "test@example.com"
        assert resp.subscription_type == "free"
        assert resp.is_active is True

    def test_subscription_types(self):
        for st in ("free", "basic", "pro", "enterprise"):
            resp = UserResponse(id="x", username="u", email="u@e.com", subscription_type=st)  # type: ignore
            assert resp.subscription_type == st

    def test_invalid_subscription_type_raises(self):
        with pytest.raises(Exception):
            UserResponse(id="x", username="u", email="u@e.com", subscription_type="platinum")  # type: ignore


class TestUserProfile:
    """UserProfile model"""

    def test_minimal(self):
        profile = UserProfile(user_id=1, username="tester")
        assert profile.user_id == 1
        assert profile.username == "tester"
        assert profile.subscription_plan == "free"
        assert profile.video_quota == 3

    def test_subscription_plans(self):
        for plan in ("free", "basic", "pro"):
            profile = UserProfile(user_id=1, username="u", subscription_plan=plan)  # type: ignore
            assert profile.subscription_plan == plan

    def test_invalid_plan_raises(self):
        with pytest.raises(Exception):
            UserProfile(user_id=1, username="u", subscription_plan="enterprise")  # type: ignore

    def test_defaults(self):
        profile = UserProfile(user_id=1, username="tester")
        assert profile.preferred_language == "zh-CN"
        assert profile.preferred_voice == "zh-CN-XiaoxiaoNeural"
        assert profile.preferred_video_ratio == "9:16"
        assert profile.videos_used_today == 0

    def test_full_profile(self):
        profile = UserProfile(
            user_id=42,
            username="pro_user",
            display_name="Pro User",
            avatar_url="https://example.com/avatar.png",
            bio="Content creator",
            website="https://example.com",
            company="Acme Inc",
            location="Shanghai",
            subscription_plan="pro",
            video_quota=50,
            videos_used_today=3,
            preferred_language="en",
            preferred_voice="en-US-JennyNeural",
            preferred_video_ratio="16:9",
        )
        assert profile.website == "https://example.com"
        assert profile.company == "Acme Inc"
        assert profile.video_quota == 50


class TestJWTPayload:
    """JWTPayload model"""

    def test_minimal(self):
        payload = JWTPayload(user_id=1, username="tester")
        assert payload.user_id == 1
        assert payload.username == "tester"
        assert payload.role == "user"

    def test_admin_role(self):
        payload = JWTPayload(user_id=2, username="admin", role="admin")
        assert payload.role == "admin"

    def test_with_expiry(self):
        payload = JWTPayload(user_id=3, username="u", exp=9999999999)
        assert payload.exp == 9999999999


class TestJWTAuthManager:
    """JWTAuthManager — token creation, validation, password utilities"""

    def test_init(self, sample_jwt_secret):
        auth = JWTAuthManager(secret_key=sample_jwt_secret)
        assert auth.secret_key == sample_jwt_secret
        assert auth.algorithm == "HS256"
        assert auth.access_token_expire_minutes == 120

    def test_init_custom_algorithm(self):
        auth = JWTAuthManager(secret_key="key", algorithm="HS512", access_token_expire_minutes=60)
        assert auth.algorithm == "HS512"
        assert auth.access_token_expire_minutes == 60

    def test_create_access_token(self, sample_jwt_secret):
        auth = JWTAuthManager(sample_jwt_secret)
        token = auth.create_access_token({"sub": "user_42", "role": "admin"})
        assert isinstance(token, str)
        assert len(token) > 20

    def test_decode_valid_token(self, sample_jwt_secret):
        auth = JWTAuthManager(sample_jwt_secret)
        token = auth.create_access_token({"sub": "user_42", "role": "admin"})
        payload = auth.decode_token(token)
        assert payload["sub"] == "user_42"
        assert payload["role"] == "admin"
        assert "exp" in payload
        assert "iat" in payload

    def test_decode_expired_token_raises(self, sample_jwt_secret):
        auth = JWTAuthManager(sample_jwt_secret)
        token = auth.create_access_token(
            {"sub": "user_1"},
            expires_delta=timedelta(seconds=-1),  # expired
        )
        with pytest.raises(ValueError, match="expired"):
            auth.decode_token(token)

    def test_decode_invalid_token_raises(self, sample_jwt_secret):
        auth = JWTAuthManager(sample_jwt_secret)
        with pytest.raises(ValueError, match="validation failed"):
            auth.decode_token("invalid.token.here")

    def test_decode_wrong_key(self, sample_jwt_secret):
        auth = JWTAuthManager(sample_jwt_secret)
        token = auth.create_access_token({"sub": "user_1"})
        wrong_auth = JWTAuthManager("different-secret-key")
        with pytest.raises(ValueError, match="validation failed"):
            wrong_auth.decode_token(token)

    def test_create_refresh_token(self, sample_jwt_secret):
        auth = JWTAuthManager(sample_jwt_secret)
        token = auth.create_refresh_token({"sub": "user_42"})
        payload = auth.decode_token(token, verify_exp=False)
        assert payload["type"] == "refresh"

    def test_get_current_user_valid(self, sample_jwt_secret):
        auth = JWTAuthManager(sample_jwt_secret)
        token = auth.create_access_token({"sub": "user_42"})
        user = auth.get_current_user(token)
        assert user["sub"] == "user_42"

    def test_get_current_user_missing_sub_raises(self, sample_jwt_secret):
        auth = JWTAuthManager(sample_jwt_secret)
        token = auth.create_access_token({"role": "admin"})  # no sub
        with pytest.raises(ValueError, match="missing"):
            auth.get_current_user(token)

    def test_hash_password(self):
        hashed = JWTAuthManager.hash_password("my_secure_password")
        assert hashed != "my_secure_password"
        assert hashed.startswith("$2b$")  # bcrypt format

    def test_verify_password_correct(self):
        hashed = JWTAuthManager.hash_password("my_secure_password")
        assert JWTAuthManager.verify_password("my_secure_password", hashed) is True

    def test_verify_password_wrong(self):
        hashed = JWTAuthManager.hash_password("correct_password")
        assert JWTAuthManager.verify_password("wrong_password", hashed) is False

    def test_create_token_with_custom_expiry(self, sample_jwt_secret):
        auth = JWTAuthManager(sample_jwt_secret)
        token = auth.create_access_token(
            {"sub": "user_1"},
            expires_delta=timedelta(hours=1),
        )
        payload = auth.decode_token(token, verify_exp=False)
        # Just verify it works without error
        assert payload["sub"] == "user_1"

    def test_decode_with_verify_exp_false(self, sample_jwt_secret):
        auth = JWTAuthManager(sample_jwt_secret)
        token = auth.create_access_token(
            {"sub": "user_1"},
            expires_delta=timedelta(seconds=-60),
        )
        # Should work when verify_exp is False
        payload = auth.decode_token(token, verify_exp=False)
        assert payload["sub"] == "user_1"
