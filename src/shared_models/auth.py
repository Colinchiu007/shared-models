"""Pydantic v2 models for authentication and user management.

Aligns with content-aggregator-shared auth module:
- UserRegisterRequest → Registration input
- UserLoginRequest → Login input
- UserResponse → User profile (public)
- TokenResponse → JWT token response
- UserProfile → Extended profile with quotas
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """User registration request."""

    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=6, max_length=128, description="Password")

    model_config = {"extra": "allow"}


class UserLoginRequest(BaseModel):
    """User login request."""

    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")

    model_config = {"extra": "allow"}


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
    """JWT token response."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: Optional[str] = Field(default=None, description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: Optional[int] = Field(default=None, description="Token expiry in seconds")
    user: Optional[UserResponse] = Field(default=None, description="User profile")

    model_config = {"extra": "allow"}


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
