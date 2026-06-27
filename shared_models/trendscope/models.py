"""TrendScope data models for cross-module use

These Pydantic v2 models serve as the data contract between TrendScope
and other modules (content-aggregator, platform-orchestrator, etc.).
"""
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class PlatformModel(BaseModel):
    code: str
    name: str
    icon_url: str = ""
    category: str = "general"
    is_active: bool = True


class TrendingTopicModel(BaseModel):
    id: int | None = None
    platform_code: str
    rank: int
    title: str
    hot_value: str
    hot_value_norm: float = 0.0
    topic_url: Optional[str] = None
    category: str = "general"
    snapshot_at: datetime | None = None


class HotArticleModel(BaseModel):
    id: int | None = None
    platform_code: str
    title: str
    summary: Optional[str] = None
    content_text: Optional[str] = None
    images: list[dict] = Field(default_factory=list)
    source_url: str
    author_name: Optional[str] = None
    author_avatar: Optional[str] = None
    read_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    # ── Extended engagement metrics (v1.5.0+) ──
    favor_count: int = 0          # 收藏数
    collected_count: int = 0      # 转采数（抖音）
    author_followers: int = 0     # 作者粉丝数
    viral_score: float = 0.0      # 归一化爆款潜力分 (0-100)
    viral_score_norm: float = 0.0 # 按平台归一化 (0-100)
    # ── ──
    publish_at: datetime | None = None
    snapshot_at: datetime | None = None


class TrendingPipelineItem(BaseModel):
    """Item sent from TrendScope to content-aggregator pipeline"""
    source_url: str
    title: str
    platform_code: str
    summary: Optional[str] = None
    author_name: Optional[str] = None
    read_count: int = 0
    like_count: int = 0


class TrendingListResponse(BaseModel):
    items: list[TrendingTopicModel]
    total: int
    page: int = 1
    page_size: int = 20
