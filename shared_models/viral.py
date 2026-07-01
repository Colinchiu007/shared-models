"""Viral content analysis data models (Pydantic v2)

Data contracts for the ViralFactorAnalyzer engine — defines the output shapes
for factor extraction, viral scoring, and trend aggregation.

These models are consumed by:
- ViralFactorAnalyzer (engine) → produces profiles & analysis
- ViralCopyGenerator (generation) → consumes factors for copywriting
- Multi-Publish / Web App (presentation) → renders analysis UI
"""

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional


# ── Enums ────────────────────────────────────────────────────────────────


class TitleStructure(str, Enum):
    """Classified title structure patterns."""

    QUESTION = "question"
    NUMBERED_LIST = "numbered_list"
    HOW_TO = "how_to"
    COMPARISON = "comparison"
    SUSPENSE = "suspense"
    DIRECT = "direct"
    CONTROVERSY = "controversy"
    STORY = "story"
    NEGATIVE = "negative"
    COMMAND = "command"
    CURIOSITY_GAP = "curiosity_gap"
    TIMELY = "timely"
    OTHER = "other"


class EmotionalTrigger(str, Enum):
    """Emotional trigger categories for content."""

    CURIOSITY = "curiosity"
    SURPRISE = "surprise"
    CONTROVERSY = "controversy"
    EMPATHY = "empathy"
    ANXIETY = "anxiety"
    FEAR = "fear"
    JOY = "joy"
    ANGER = "anger"
    INSPIRATION = "inspiration"
    NONE = "none"


class ContentStructure(str, Enum):
    """Body text structure patterns."""

    LIST = "list"
    STORY = "story"
    TUTORIAL = "tutorial"
    OPINION = "opinion"
    EMOTIONAL = "emotional"
    NEWS = "news"
    REVIEW = "review"
    GUIDE = "guide"
    OTHER = "other"


# ── Core models ──────────────────────────────────────────────────────────


class ViralFactor(BaseModel):
    """A single viral factor dimension with score and evidence."""

    name: str = Field(..., description="Factor name, e.g. 'title_structure', 'emotion'")
    label: str = Field(default="", description="Human-readable label in Chinese")
    score: float = Field(default=0.0, ge=0.0, le=1.0, description="Normalized score 0-1")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Detection confidence")
    evidence: list[str] = Field(default_factory=list, description="Supporting evidence snippets")
    details: dict = Field(default_factory=dict, description="Extra factor-specific data")


class TitleAnalysis(BaseModel):
    """Extracted title structure and pattern analysis."""

    title: str = Field(..., description="Original title text")
    structure: TitleStructure = Field(default=TitleStructure.OTHER)
    length: int = Field(default=0, description="Character count")
    word_count: int = Field(default=0)
    has_numbers: bool = Field(default=False)
    has_questions: bool = Field(default=False)
    has_emojis: bool = Field(default=False)
    has_colon: bool = Field(default=False)
    has_power_words: list[str] = Field(default_factory=list)
    emotion: EmotionalTrigger = Field(default=EmotionalTrigger.NONE)
    confidence: float = Field(default=0.0)


class EngagementMetrics(BaseModel):
    """Raw and normalized engagement metrics."""

    likes: int = 0
    comments: int = 0
    shares: int = 0
    favorites: int = 0
    views: int = 0

    # Normalized (0-100, platform-aware)
    likes_norm: float = 0.0
    comments_norm: float = 0.0
    shares_norm: float = 0.0
    favorites_norm: float = 0.0

    # Aggregated
    total_engagement: int = 0
    engagement_rate: float = 0.0  # per-view rate if views available
    viral_score: float = 0.0  # weighted combination


class ArticleViralProfile(BaseModel):
    """Per-article viral factor breakdown."""

    # Identity
    platform_code: str = ""
    title: str = ""
    author_name: str = ""
    author_followers: int = 0
    source_url: str = ""
    category: str = "general"

    # Analysis
    title_analysis: TitleAnalysis = Field(default_factory=TitleAnalysis)
    engagement: EngagementMetrics = Field(default_factory=EngagementMetrics)
    factors: list[ViralFactor] = Field(default_factory=list)

    # Summary
    overall_score: float = 0.0  # 0-100
    rank: int = 0  # Position in trending list
    snapshot_at: Optional[datetime] = None


class ViralAnalysisResult(BaseModel):
    """Full analysis result for a topic or set of articles."""

    topic: str = Field(..., description="Analyzed topic or keyword")
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now().astimezone())

    # Overall
    overall_score: float = 0.0
    trend_direction: str = "stable"  # rising / stable / declining
    confidence: float = 0.0

    # Factor breakdown
    factors: list[ViralFactor] = Field(default_factory=list)

    # Per-article profiles
    articles: list[ArticleViralProfile] = Field(default_factory=list)

    # Platform comparison
    platform_scores: dict[str, float] = Field(default_factory=dict)

    # Generation suggestions
    suggested_structures: list[dict] = Field(
        default_factory=list,
        description="Recommended title structures with expected lift",
    )
    suggested_angles: list[str] = Field(
        default_factory=list,
        description="Alternative writing angles for this topic",
    )


# ── Aggregated models ────────────────────────────────────────────────────


class TrendingInsights(BaseModel):
    """Aggregated platform-level trending insights."""

    platform_code: str = ""
    snapshot_at: datetime = Field(default_factory=lambda: datetime.now().astimezone())
    total_items: int = 0

    # Category distribution
    category_distribution: dict[str, int] = Field(default_factory=dict)

    # Title pattern distribution
    title_structure_distribution: dict[str, int] = Field(default_factory=dict)

    # Emotion distribution
    emotion_distribution: dict[str, int] = Field(default_factory=dict)

    # Top topics with scores
    top_topics: list[dict] = Field(default_factory=list)

    # Rising keywords (word frequency delta)
    rising_keywords: list[dict] = Field(default_factory=list)


# ── Configuration ────────────────────────────────────────────────────────


class ViralScoringConfig(BaseModel):
    """Configurable weights for viral score computation.

    The viral score is computed as:
        score = w_linear * linear_component + w_log * log_component

    Where linear_component is a weighted sum of normalized engagement metrics
    and log_component applies log-scaling to reduce outlier effects.
    """

    # Engagement weights (must sum to 1.0 for linear part)
    weight_likes: float = Field(default=0.35, ge=0.0, le=1.0)
    weight_comments: float = Field(default=0.30, ge=0.0, le=1.0)
    weight_shares: float = Field(default=0.25, ge=0.0, le=1.0)
    weight_favorites: float = Field(default=0.10, ge=0.0, le=1.0)

    # Score blending
    w_linear: float = Field(default=0.6, ge=0.0, le=1.0)
    w_log: float = Field(default=0.3, ge=0.0, le=1.0)
    w_authority: float = Field(default=0.1, ge=0.0, le=1.0)

    # Normalization
    norm_ceiling: int = Field(default=100000, description="Max raw value for normalization")
    log_base: float = Field(default=10.0)

    # Platform-specific ceilings (likes, comments, shares)
    platform_ceilings: dict[str, list[int]] = Field(default_factory=lambda: {
        "xiaohongshu": [50000, 10000, 20000],
        "douyin": [100000, 20000, 50000],
        "reddit": [50000, 10000, 5000],
    })

    def validate_weights(self) -> bool:
        """Ensure engagement weights sum to ~1.0."""
        total = (
            self.weight_likes
            + self.weight_comments
            + self.weight_shares
            + self.weight_favorites
        )
        return 0.99 <= total <= 1.01
