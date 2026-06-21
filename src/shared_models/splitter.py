"""Pydantic v2 models for smart-sentence-splitter data structures.

Mirrors the dataclass types from splitter.models:
- SentenceBlock → SentenceBlock
- SplitResult → SplitResult
- SceneSegment → SceneSegment
- SubtitleBlock → SubtitleBlock
- EraInfo → EraInfo

All models use extra="allow" for forward compatibility with v0.7+ fields.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class SentenceBlock(BaseModel):
    """A single split sentence with metadata."""

    text: str = Field(..., min_length=1, description="Sentence text")
    index: int = Field(..., ge=0, description="Global index (0-based)")
    char_count: int = Field(default=0, description="Character count (auto-computed as len(text))")
    word_count: int = Field(default=0, description="Word count (tokenizer-dependent)")
    words: List[str] = Field(default_factory=list, description="Tokenized words")
    pos_tags: List[str] = Field(default_factory=list, description="POS tags (parallel to words)")
    language: str = Field(default="zh", description="Detected language: zh/en/ja/mixed")
    tier: str = Field(default="tier3_rule", description="Actual tier used: tier1_llm/tier2_semantic/tier3_rule")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score 0-1")
    is_topic_boundary: bool = Field(default=False, description="TextTiling topic boundary flag")
    topic_depth_score: float = Field(default=0.0, description="Boundary depth score")
    length_status: Literal["ok", "too_short", "too_long"] = Field(
        default="ok", description="Length-check status (v0.6)"
    )
    length_strategy_applied: Literal["none", "A", "B"] = Field(
        default="none", description="Length-control strategy applied (v0.6)"
    )

    model_config = {"extra": "allow"}


class EraInfo(BaseModel):
    """Era detection result for Chinese text."""

    era: str = Field(..., description="Era classification: modern/ancient/mixed")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
    keywords: List[str] = Field(default_factory=list, description="Matching keywords")

    @field_validator("era")
    @classmethod
    def validate_era(cls, v: str) -> str:
        valid = frozenset({"modern", "ancient", "mixed"})
        if v not in valid:
            raise ValueError(f"era must be one of {valid}, got {v!r}")
        return v

    model_config = {"extra": "allow"}


class SubtitleBlock(BaseModel):
    """A single subtitle display block with timing info."""

    text: str = Field(..., min_length=1, description="Subtitle text")
    display_order: int = Field(..., ge=0, description="Display order within scene (0-based)")
    start_time: float = Field(..., ge=0.0, description="Start time relative to scene start (sec)")
    duration: float = Field(..., ge=0.0, description="Display duration (sec)")
    parent_segment_id: int = Field(..., ge=0, description="Parent scene's segment_id")

    model_config = {"extra": "allow"}


class SceneSegment(BaseModel):
    """A scene grouping containing sentences and subtitle blocks."""

    text: str = Field(..., description="Concatenated scene text")
    segment_id: int = Field(..., description="Global segment index")
    estimated_duration: float = Field(..., description="Estimated duration in seconds")
    target_words: int = Field(..., description="Target word count")
    sentences: List[SentenceBlock] = Field(default_factory=list, description="Contained sentences")
    era_info: Optional[EraInfo] = Field(default=None, description="Era detection result")
    subtitles: List[SubtitleBlock] = Field(
        default_factory=list, description="Subtitle blocks within this scene"
    )
    # v0.7+ fields
    characters: List[str] = Field(default_factory=list, description="Character names (v0.7)")
    setting: str = Field(default="", description="Scene setting (v0.7)")
    mood: str = Field(default="", description="Inferred mood (v0.7)")
    story_phase: str = Field(default="", description="Story phase label (v0.7)")

    model_config = {"extra": "allow"}


class SplitResult(BaseModel):
    """Top-level result from SmartSentenceSplitter.split()."""

    sentences: List[SentenceBlock] = Field(default_factory=list, description="All split sentences")
    scenes: List[SceneSegment] = Field(
        default_factory=list, description="Scene groupings with subtitles"
    )
    tier_used: str = Field(default="tier3_rule", description="Actual tier used")
    language: str = Field(default="zh", description="Detected language")
    total_duration: float = Field(default=0.0, description="Sum of scene durations (sec)")
    total_words: int = Field(default=0, description="Total character count across scenes")
    total_scenes: int = Field(default=0, description="Number of scenes")
    config_snapshot: Dict[str, Any] = Field(
        default_factory=dict, description="Config used for this split"
    )
    script_analysis: Optional[Dict[str, Any]] = Field(
        default=None, description="Script analysis result (v0.7)"
    )

    model_config = {"extra": "allow"}
