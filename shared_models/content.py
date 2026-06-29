"""Content aggregator pipeline data models — aligned with content-aggregator API.

These models serve as the data contract between content-aggregator and other
pipeline stages (trendscope -> content-aggregator -> smart-sentence-splitter).

Aligned with: content-aggregator/backend/app/schemas/article.py
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# -- Collection Stage --------------------------------------------------------


class CollectRequest(BaseModel):
    """URL content collection request.

    Mirrors: content-aggregator CollectURLRequest
    """
    url: str = Field(..., description="Source URL to fetch")
    source: str = Field(default="manual", description="Source identifier (manual/trendscope/rpa)")
    platform: Optional[str] = Field(default=None, description="Platform code if from trendscope")


class CollectResult(BaseModel):
    """URL content collection result.

    Mirrors: content-aggregator CollectResponse
    """
    title: str = Field(default="", description="Collected article title")
    content: str = Field(default="", description="Collected article content (plain text)")
    source_url: str = Field(..., description="Original source URL")
    author: Optional[str] = Field(default=None, description="Original author name")
    word_count: int = Field(default=0, description="Word count of collected content")


# -- Rewrite Stage ---------------------------------------------------------


class RewriteRequest(BaseModel):
    """AI rewrite request (pipeline contract — uses content directly, not article_id).

    Mirrors: content-aggregator RewriteRequest
    """
    content: str = Field(..., min_length=1, description="Source content to rewrite")
    title: str = Field(default="", description="Original title")
    style: str = Field(default="default", description="Rewrite style: casual / formal / eye-catching / deep-analysis")
    length: str = Field(default="medium", description="Length strategy: keep / compress / expand / short / medium / long")
    target_platform: Optional[str] = Field(default=None, description="Target platform for style tuning")
    seo_optimize: bool = Field(default=False, description="Enable SEO optimization")


class RewriteResult(BaseModel):
    """AI rewrite result.

    Mirrors: content-aggregator RewriteResponse (with added title)
    """
    rewritten_title: str = Field(default="", description="AI-optimized title")
    rewritten_content: str = Field(..., description="Rewritten content")
    style: str = Field(default="default", description="Applied rewrite style")
    word_count: int = Field(default=0, description="Word count of rewritten content")
    model_used: str = Field(default="", description="LLM model used")
    created_at: datetime = Field(default_factory=datetime.now)
