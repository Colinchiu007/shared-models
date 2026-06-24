"""Auth-related data models"""
from pydantic import BaseModel, Field


class UserLoginRequest(BaseModel):
    account: str = Field(..., min_length=1, description="Username, email, or phone")
    password: str = Field(..., min_length=1)
    login_method: str = Field(default="password", pattern="^(password|sms)$")


class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    email: str | None = None
    phone: str | None = None
    password: str = Field(..., min_length=8)
    verify_code: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int = 7200
    user_id: int | None = None
    username: str | None = None
    role: str = "user"


class JWTPayload(BaseModel):
    """Standard JWT payload used across all services"""
    user_id: int
    username: str
    role: str = "user"
    exp: int | None = None
