"""Auth-related data models - consolidated (INT-002: merged from src/)

Models imported from src/shared_models/auth.py:
- RefreshRequest: token refresh request
- UserResponse: public user profile (safe for API responses)
- UserProfile: extended profile with quotas and preferences
- JWTAuthManager: unified JWT + password utility class
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Literal, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field

# ── Module-level password context (singleton) ─────────────────────────
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserLoginRequest(BaseModel):
    account: str = Field(..., min_length=1, description="Username, email, or phone")
    password: str = Field(..., min_length=1)
    login_method: str = Field(default="password", pattern="^(password|sms)$")


class LoginRequest(BaseModel):
    """Login request — platform-orchestrator compatible.

    Mirrors: platform-orchestrator/routers/auth.py LoginRequest
    """
    username: str = Field(...)
    password: str = Field(...)


class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    email: str | None = None
    phone: str | None = None
    password: str = Field(..., min_length=8)
    verify_code: str | None = None


class RegisterRequest(BaseModel):
    """Registration request — platform-orchestrator compatible.

    Mirrors: platform-orchestrator/routers/auth.py RegisterRequest
    Username must match: letters, digits, underscore only.
    """
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email: str | None = Field(None)
    password: str = Field(..., min_length=6, max_length=128)


class RefreshRequest(BaseModel):
    """Token refresh request."""

    refresh_token: str = Field(..., description="Refresh token")

    model_config = {"extra": "allow"}


class UserResponse(BaseModel):
    """Public user profile (safe for API response)."""

    id: str = Field(..., description="User UUID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    subscription_type: Literal["free", "basic", "pro", "enterprise"] = Field(
        default="free", description="Subscription tier"
    )
    created_at: Optional[datetime] = Field(default=None, description="Registration date")
    is_active: bool = Field(default=True, description="Account active status")

    model_config = {"from_attributes": True, "extra": "allow"}


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int = 7200
    user_id: int | None = None
    username: str | None = None
    role: str = "user"


class AuthTokenResponse(BaseModel):
    """Token response — platform-orchestrator compatible.

    Mirrors: platform-orchestrator/routers/auth.py TokenResponse
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class UserProfile(BaseModel):
    """Extended user profile with quotas and preferences."""

    user_id: int = Field(..., description="Internal user ID")
    username: str = Field(..., description="Username")
    display_name: Optional[str] = Field(default=None, description="Display name")
    avatar_url: Optional[str] = Field(default=None, description="Avatar URL")
    bio: Optional[str] = Field(default=None, description="Bio text")
    website: Optional[str] = Field(default=None, description="Personal website")
    company: Optional[str] = Field(default=None, description="Company name")
    location: Optional[str] = Field(default=None, description="Location")
    subscription_plan: Literal["free", "basic", "pro"] = Field(
        default="free", description="Subscription plan"
    )
    video_quota: int = Field(default=3, description="Daily video generation quota")
    videos_used_today: int = Field(default=0, description="Videos generated today")
    preferred_language: str = Field(default="zh-CN", description="UI language preference")
    preferred_voice: str = Field(
        default="zh-CN-XiaoxiaoNeural", description="TTS voice preference"
    )
    preferred_video_ratio: str = Field(default="9:16", description="Video aspect ratio")

    model_config = {"from_attributes": True, "extra": "allow"}


class JWTPayload(BaseModel):
    """Standard JWT payload used across all services"""
    user_id: int
    username: str
    role: str = "user"
    exp: int | None = None


class JWTAuthManager:
    """Unified JWT authentication manager.

    Provides token creation/validation and password hashing.
    Designed to be instantiated once per service with its config,
    then passed as a dependency.

    Usage:
        auth = JWTAuthManager(secret_key="...", algorithm="HS256")
        token = auth.create_access_token({"sub": user_id})
        payload = auth.decode_token(token)
        user = auth.get_current_user(credentials)  # FastAPI dependency
        hashed = JWTAuthManager.hash_password("plain")
        ok = JWTAuthManager.verify_password("plain", hashed)
    """

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 120,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes

    # ── Token creation ────────────────────────────────────────────────

    def create_access_token(
        self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (
            expires_delta or timedelta(minutes=self.access_token_expire_minutes)
        )
        to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(
        self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a refresh token (longer-lived, with type marker)."""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (
            expires_delta or timedelta(days=7)
        )
        to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc), "type": "refresh"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    # ── Token validation ──────────────────────────────────────────────

    def decode_token(self, token: str, verify_exp: bool = True) -> Dict[str, Any]:
        """Decode and validate a JWT token. Raises ValueError on failure."""
        try:
            return jwt.decode(
                token, self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": verify_exp},
            )
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except JWTError as e:
            raise ValueError(f"Token validation failed: {e}")

    def get_current_user(self, token: str) -> Dict[str, Any]:
        """Extract user payload from a Bearer token string.

        Returns the decoded payload dict.
        Raises ValueError if token is invalid or missing 'sub' claim.
        """
        payload = self.decode_token(token)
        if payload.get("sub") is None:
            raise ValueError("Token missing 'sub' claim")
        return payload

    # ── Password utilities (static, no config needed) ─────────────────

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plain-text password using bcrypt."""
        return _pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain-text password against a bcrypt hash."""
        return _pwd_context.verify(plain_password, hashed_password)
