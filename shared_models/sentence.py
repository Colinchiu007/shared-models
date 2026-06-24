"""Smart sentence splitter data models — aligned with splitter dataclass output.

These Pydantic models mirror the splitter's dataclass models (SentenceBlock,
SceneSegment, SubtitleBlock, SplitResult) so that orchestrator and other
consumers can validate splitter output without importing splitter directly.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class SentenceBlock(BaseModel):
    """Single sentence with full metadata.

    Mirrors: splitter.models.sentence.SentenceBlock (dataclass)
    """
    text: str
    index: int
    char_count: int = 0
    word_count: int = 0
    words: list[str] = Field(default_factory=list)
    pos_tags: list[str] = Field(default_factory=list)
    language: str = "zh"
    tier: str = "tier3_rule"
    confidence: float = 1.0
    is_topic_boundary: bool = False
    topic_depth_score: float = 0.0
    length_status: str = "ok"
    length_strategy_applied: str = "none"


class SubtitleBlock(BaseModel):
    """Subtitle block for video generation.

    Mirrors: splitter.models.subtitle.SubtitleBlock (dataclass)
    """
    text: str
    display_order: int
    start_time: float
    duration: float
    parent_segment_id: int


class SceneSegment(BaseModel):
    """Scene segment containing multiple sentences and subtitles.

    Mirrors: splitter.models.scene.SceneSegment (dataclass)
    """
    text: str
    segment_id: int
    estimated_duration: float
    target_words: int
    sentences: list[SentenceBlock] = Field(default_factory=list)
    era_info: dict | None = None
    subtitles: list[SubtitleBlock] = Field(default_factory=list)
    characters: list[str] = Field(default_factory=list)
    setting: str = ""
    mood: str = ""
    story_phase: str = ""


class SplitResult(BaseModel):
    """Top-level result from sentence splitter.

    Mirrors: splitter.models.result.SplitResult (dataclass)
    """
    sentences: list[SentenceBlock] = Field(default_factory=list)
    scenes: list[SceneSegment] = Field(default_factory=list)
    tier_used: str = "tier3_rule"
    language: str = "zh"
    total_duration: float = 0.0
    total_words: int = 0
    total_scenes: int = 0
    config_snapshot: dict = Field(default_factory=dict)
    script_analysis: dict | None = None
    # Backward-compat aliases for consumers that expected the old model:
    model_used: str = ""
    era_info: dict | None = None
