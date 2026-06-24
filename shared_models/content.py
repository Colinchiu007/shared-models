"""Content aggregator data models"""
from pydantic import BaseModel, Field
from datetime import datetime


class ContentFetchRequest(BaseModel):
    url: str = Field(..., description="Source URL to fetch and rewrite")
    source: str = Field(default="manual", description="Source identifier (manual/trendscope/rpa)")
    platform: str | None = None
    style: str = Field(default="default", description="Rewrite style")


class RewriteConfig(BaseModel):
    style: str = "公众号"  # 公众号/知乎/小红书/短视频文案
    length: str = "medium"  # short/medium/long
    target_platform: str | None = None


class RewriteResult(BaseModel):
    original_url: str
    rewritten_title: str
    rewritten_content: str
    style: str
    word_count: int
    model_used: str
    created_at: datetime
