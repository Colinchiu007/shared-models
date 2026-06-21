"""Pydantic v2 models for prompt-engine data structures.

Mirrors the Pydantic models from prompt_engine.models:
- PlatformType, StyleType, StyleCategory → Enums
- OptimizeRequest, OptimizeResult → Main I/O
- ReverseRequest, ReverseResult → Reverse engineering
- StyleCategoryResult → Classification output
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ── Platform & Style Enums ──────────────────────────────────────────────────


class PlatformType(str, Enum):
    """Target image generation platform."""

    MIDJOURNEY = "midjourney"
    STABLE_DIFFUSION = "stable_diffusion"
    DALLE = "dalle"
    TONGYI = "tongyi"
    YIZHANG = "yizhang"
    JIMENG = "jimeng"
    GENERIC = "generic"


class StyleType(str, Enum):
    """Artistic style for prompt optimization."""

    REALISTIC = "realistic"
    CARTOON = "cartoon"
    ANIME = "anime"
    OIL_PAINTING = "oil_painting"
    WATERCOLOR = "watercolor"
    PIXEL = "pixel"
    CYBERPUNK = "cyberpunk"
    FANTASY = "fantasy"
    PHOTOGRAPHY = "photography"
    _3D_RENDER = "3d_render"
    MINIMALIST = "minimalist"
    ABSTRACT = "abstract"
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"


class StyleCategory(str, Enum):
    """MJ style dimension categories (25 dimensions)."""

    LIGHTING = "lighting"
    MATERIAL_PROPERTIES = "material_properties"
    MATERIALS = "materials"
    DIMENSIONALITY = "dimensionality"
    COLORS_AND_PALETTES = "colors_and_palettes"
    COMBINATIONS = "combinations"
    CAMERA = "camera"
    PERSPECTIVE = "perspective"
    STRUCTURAL_MODIFICATION = "structural_modification"
    NATURE_AND_ANIMALS = "nature_and_animals"
    OBJECTS = "objects"
    OUTER_SPACE = "outer_space"
    GEOMETRY = "geometry"
    GEOGRAPHY_AND_CULTURE = "geography_and_culture"
    DRAWING_AND_ART_MEDIUMS = "drawing_and_art_mediums"
    SFX_AND_SHADERS = "sfx_and_shaders"
    THEMES = "themes"
    INTANGIBLES = "intangibles"
    TV_AND_MOVIES = "tv_and_movies"
    SONG_LYRICS = "song_lyrics"
    DESIGN_STYLES = "design_styles"
    DIGITAL = "digital"
    EXPERIMENTAL = "experimental"
    EMOJIS = "emojis"
    MISCELLANEOUS = "miscellaneous"


# ── Request Models ──────────────────────────────────────────────────────────


class OptimizeRequest(BaseModel):
    """Request to optimize a prompt for image generation."""

    prompt: str = Field(..., min_length=1, max_length=2000, description="Raw prompt text")
    platform: PlatformType = Field(default=PlatformType.GENERIC, description="Target platform")
    style: Optional[StyleType] = Field(default=None, description="Artistic style override")
    creative_level: int = Field(default=5, ge=1, le=10, description="Creativity 1-10")
    max_length: int = Field(default=300, ge=50, le=2000, description="Max output length")
    negative_prompt: Optional[str] = Field(
        default=None, max_length=500, description="Elements to avoid"
    )
    num_candidates: int = Field(default=1, ge=1, le=5, description="A/B test candidates")
    auto_detect_style: bool = Field(default=True, description="Auto-detect style from prompt")
    context: Optional[Dict[str, Any]] = Field(
        default=None, description="Character consistency context dict"
    )

    model_config = {"extra": "allow"}


class ReverseRequest(BaseModel):
    """Request to reverse-engineer a prompt from image URL."""

    prompt: str = Field(..., min_length=1, max_length=2000, description="Image description")
    platform: PlatformType = Field(default=PlatformType.GENERIC, description="Target platform")

    model_config = {"extra": "allow"}


# ── Response / Result Models ────────────────────────────────────────────────


class StyleCategoryResult(BaseModel):
    """Style classification result."""

    categories: List[str] = Field(default_factory=list, description="Detected category names")
    keywords_found: List[str] = Field(
        default_factory=list, description="Matched keywords per category"
    )
    method: str = Field(
        default="", description="Classification method: keyword_match/llm_classify/vector_rag"
    )
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence 0-1")

    model_config = {"extra": "allow"}


class OptimizeResult(BaseModel):
    """Result from prompt optimization."""

    optimized_prompt: str = Field(..., description="Optimized prompt text")
    platform: PlatformType = Field(..., description="Actual platform used")
    style: Optional[StyleType] = Field(default=None, description="Applied style")
    model_used: str = Field(default="", description="LLM model name")
    tokens_used: int = Field(default=0, description="Tokens consumed")
    duration_ms: float = Field(default=0.0, description="Processing time milliseconds")
    candidates: List[str] = Field(
        default_factory=list, description="A/B test candidate prompts"
    )
    error: Optional[str] = Field(default=None, description="Error message if failed")
    detected_categories: Optional[StyleCategoryResult] = Field(
        default=None, description="Auto-detected style categories"
    )

    model_config = {"extra": "allow"}


class ReverseResult(BaseModel):
    """Result from reverse engineering a prompt."""

    analyzed_prompt: str = Field(..., description="Generated prompt from image analysis")
    platform: PlatformType = Field(..., description="Target platform")
    inferred_style: Optional[StyleType] = Field(default=None, description="Inferred style")
    keywords: List[str] = Field(default_factory=list, description="Extracted keywords")
    model_used: str = Field(default="", description="Vision model used")
    error: Optional[str] = Field(default=None, description="Error message if failed")

    model_config = {"extra": "allow"}
