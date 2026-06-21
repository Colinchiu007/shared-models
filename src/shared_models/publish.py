"""Pydantic v2 models for multi-platform publishing.

Aligns with Multi-Publish Python backend:
- PublishPlatformType → Supported platform enum
- PublishTaskStatus → Task lifecycle states
- PublishResult → Per-platform publish result
- PublishTask → Full publish task with multi-platform support
- PlatformAccount → Platform account configuration
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, model_validator


class PublishPlatformType(str, Enum):
    """Supported publishing platforms."""

    WECHAT_MP = "wechat_mp"
    ZHIHU = "zhihu"
    WEIBO = "weibo"
    DOUYIN = "douyin"
    XIAOHONGSHU = "xiaohongshu"
    TOUTIAO = "toutiao"
    BAIDU = "baidu"
    BILIBILI = "bilibili"
    KUAISHOU = "kuaishou"
    JIANSHU = "jianshu"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"


class PublishTaskStatus(str, Enum):
    """Publish task lifecycle states."""

    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PublishResult(BaseModel):
    """Per-platform publish result."""

    success: bool = Field(..., description="Whether publish succeeded")
    platform: PublishPlatformType = Field(..., description="Target platform")
    article_id: Optional[str] = Field(default=None, description="Platform-side article ID")
    url: Optional[str] = Field(default=None, description="Published article URL")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    duration: Optional[float] = Field(default=None, description="Publish duration seconds")

    model_config = {"extra": "allow"}


class PublishTask(BaseModel):
    """A multi-platform publish task."""

    id: str = Field(..., description="Task ID")
    title: str = Field(..., description="Article title")
    content: str = Field(..., description="Article content")
    platforms: List[PublishPlatformType] = Field(
        ..., min_length=1, description="Target platforms"
    )
    status: PublishTaskStatus = Field(
        default=PublishTaskStatus.PENDING, description="Current status"
    )
    results: Dict[str, PublishResult] = Field(
        default_factory=dict, description="Per-platform results"
    )
    scheduled_at: Optional[datetime] = Field(default=None, description="Scheduled publish time")
    retry_count: int = Field(default=0, description="Number of retries")
    max_retries: int = Field(default=3, description="Max retry attempts")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Extra metadata (cover, tags, etc.)"
    )
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")

    @model_validator(mode="after")
    def check_platforms_not_empty(self) -> "PublishTask":
        if not self.platforms:
            raise ValueError("platforms must not be empty")
        return self

    model_config = {"extra": "allow"}


class PlatformAccount(BaseModel):
    """Platform account configuration."""

    id: str = Field(..., description="Account ID")
    platform: PublishPlatformType = Field(..., description="Platform")
    name: str = Field(..., description="Account display name")
    config: Dict[str, Any] = Field(
        default_factory=dict, description="Platform-specific config (API keys, cookies, etc.)"
    )
    is_active: bool = Field(default=True, description="Whether account is active")
    last_validated: Optional[datetime] = Field(
        default=None, description="Last credential validation time"
    )
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")

    model_config = {"extra": "allow"}
