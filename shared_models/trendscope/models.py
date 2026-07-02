"""TrendScope data models for cross-module use

These Pydantic v2 models serve as the data contract between TrendScope
and other modules (content-aggregator, platform-orchestrator, etc.).
"""
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class PlatformModel(BaseModel):
    id: int
    code: str
    name: str
    icon_url: str = ""
    category: str = "general"
    is_active: bool = True


class TrendingTopicModel(BaseModel):
    """Trending topic — matches trendscope _serialize_topic() output.

    Mirrors: trendscope/api/services/trending_service.py _serialize_topic()
    """
    id: int | None = None
    platform: dict = Field(default_factory=dict, description="Nested platform {code, name, icon_url}")
    rank: int
    title: str
    hot_value: str
    hot_value_norm: float = 0.0
    topic_url: str = ""
    category: str = "general"
    snapshot_at: str = """"""


class HotArticleModel(BaseModel):
    """Hot article — matches trendscope _serialize_article() output.

    Mirrors: trendscope/api/services/article_service.py _serialize_article()
    """
    id: int | None = None
    platform: dict = Field(default_factory=dict, description="Nested platform {code, name, icon_url}")
    title: str = ""
    summary: str = ""
    content_text: Optional[str] = None
    images: list[dict] = Field(default_factory=list)
    video_url: str = ""
    source_url: str = ""
    author_name: str = ""
    author_avatar: str = ""
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
    publish_at: str = ""
    snapshot_at: str = ""


class TrendingPipelineItem(BaseModel):
    """Item sent from TrendScope to content-aggregator pipeline"""
    source_url: str
    title: str
    platform: dict = Field(default_factory=dict, description="Nested platform {code, name}")
    summary: str = ""
    author_name: str = ""
    read_count: int = 0
    like_count: int = 0


class TrendingListResponse(BaseModel):
    """Paginated trending topic list — matches trendscope GET /trending response."""
    items: list[TrendingTopicModel]
    total: int
    page: int = 1
    page_size: int = 20


class HotArticleListResponse(BaseModel):
    """Paginated hot article list — matches trendscope GET /articles response."""
    items: list[HotArticleModel]
    total: int
    page: int = 1
    page_size: int = 20


class ApiResponse(BaseModel):
    """Standard API response wrapper — matches trendscope {code, data, pagination}."""
    code: int = 0
    message: str = "success"
    data: dict | None = None
    pagination: dict | None = None
