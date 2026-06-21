"""Pydantic v2 models for article/content management.

Aligns with content-aggregator v2 backend schemas:
- ArticleCreate → ArticleCreate (source fields)
- ArticleListItem → ArticleListItem (summary view)
- ArticleResponse → ArticleResponse (full detail)
- RewriteRequest → RewriteRequest (style/length/seo)
- CollectURLRequest → CollectURLRequest (URL input)
- CollectResponse → CollectResponse (fetch result)
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator


# ── Validated Constants ─────────────────────────────────────────────────────

REWRITE_STYLES = frozenset({"轻松易懂", "正式严谨", "吸引眼球", "深度分析"})
REWRITE_LENGTHS = frozenset({"keep", "compress", "expand"})
SOURCE_TYPES = frozenset({"url", "text", "file"})


# ── Request Models ──────────────────────────────────────────────────────────


class ArticleCreate(BaseModel):
    """Create a new article from a source."""

    source_type: Literal["url", "text", "file"] = Field(
        ..., description="Source type: url/text/file"
    )
    source_content: Optional[str] = Field(default=None, description="Raw text content")
    source_url: Optional[str] = Field(default=None, description="Source URL")

    @field_validator("source_type")
    @classmethod
    def validate_source_type(cls, v: str) -> str:
        if v not in SOURCE_TYPES:
            raise ValueError(f"source_type must be one of {SOURCE_TYPES}, got {v!r}")
        return v

    model_config = {"extra": "allow"}


class CollectURLRequest(BaseModel):
    """Request to collect content from a URL."""

    url: HttpUrl = Field(..., description="URL to fetch content from")

    model_config = {"extra": "allow"}


class RewriteRequest(BaseModel):
    """Request to AI-rewrite an article."""

    article_id: str = Field(..., description="Article ID to rewrite")
    style: str = Field(..., description="Rewrite style")
    length: str = Field(default="keep", description="Length strategy: keep/compress/expand")
    seo_optimize: bool = Field(default=False, description="Apply SEO optimization")

    @field_validator("style")
    @classmethod
    def validate_style(cls, v: str) -> str:
        if v not in REWRITE_STYLES:
            raise ValueError(f"style must be one of {REWRITE_STYLES}, got {v!r}")
        return v

    @field_validator("length")
    @classmethod
    def validate_length(cls, v: str) -> str:
        if v not in REWRITE_LENGTHS:
            raise ValueError(f"length must be one of {REWRITE_LENGTHS}, got {v!r}")
        return v

    model_config = {"extra": "allow"}


# ── Response Models ─────────────────────────────────────────────────────────


class ArticleListItem(BaseModel):
    """Summary view of an article for list display."""

    id: str = Field(..., description="Article UUID")
    source_type: str = Field(..., description="Source type")
    source_url: Optional[str] = Field(default=None, description="Source URL")
    source_content: Optional[str] = Field(default=None, description="Source content preview")
    rewrite_style: Optional[str] = Field(default=None, description="Rewriting style used")
    rewrite_length: Optional[str] = Field(default=None, description="Rewriting length strategy")
    word_count_original: Optional[int] = Field(default=None, description="Original word count")
    word_count_result: Optional[int] = Field(default=None, description="Result word count")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")

    model_config = {"from_attributes": True, "extra": "allow"}


class ArticleResponse(BaseModel):
    """Full article detail with rewrite result."""

    id: str = Field(..., description="Article UUID")
    user_id: str = Field(..., description="Owner user ID")
    source_type: str = Field(..., description="Source type")
    source_content: Optional[str] = Field(default=None, description="Raw source content")
    source_url: Optional[str] = Field(default=None, description="Source URL")
    rewrite_style: Optional[str] = Field(default=None, description="Rewrite style")
    rewrite_length: Optional[str] = Field(default=None, description="Length strategy")
    result_content: Optional[str] = Field(default=None, description="Rewritten content")
    word_count_original: Optional[int] = Field(default=None, description="Original words")
    word_count_result: Optional[int] = Field(default=None, description="Result words")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")

    model_config = {"from_attributes": True, "extra": "allow"}


class CollectResponse(BaseModel):
    """Result from URL content collection."""

    title: str = Field(..., description="Page title")
    content: str = Field(..., description="Extracted content")
    author: Optional[str] = Field(default=None, description="Author name if available")
    word_count: int = Field(default=0, description="Word count")
    source_url: Optional[str] = Field(default=None, description="Original URL")

    model_config = {"extra": "allow"}
