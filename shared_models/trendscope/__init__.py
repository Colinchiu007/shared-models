"""TrendScope shared Pydantic models for cross-module integration."""
from shared_models.trendscope.models import (
    ApiResponse,
    HotArticleListResponse,
    HotArticleModel,
    PlatformModel,
    TrendingListResponse,
    TrendingPipelineItem,
    TrendingTopicModel,
)

__all__ = [
    "ApiResponse",
    "HotArticleListResponse",
    "HotArticleModel",
    "PlatformModel",
    "TrendingListResponse",
    "TrendingPipelineItem",
    "TrendingTopicModel",
]
