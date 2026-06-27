"""Auth-related data models - consolidated (INT-002: merged from src/)

Models imported from src/shared_models/auth.py:
- RefreshRequest: token refresh request
- UserResponse: public user profile (safe for API responses)
- UserProfile: extended profile with quotas and preferences
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field


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
