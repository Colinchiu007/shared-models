"""shared-models: Unified Pydantic v2 data contracts

All modules in the one-stop video generation platform import from this package
to ensure consistent data structures across process boundaries.

Week 0 Interface Freeze (2026-06-25):
  - ContentPacket ─ unified pipeline carrier (trendscope→aggregator→splitter→prompt→Story2Video→publish)
  - SplitResult (with SentenceBlock/SceneSegment) ─ smart-sentence-splitter → prompt-engine
  - VideoAsset (with ScenePrompt) ─ prompt-engine → Story2Video
"""

from __future__ import annotations

# ── Auth ──────────────────────────────────────────────────────────────
from shared_models.auth import (
    JWTAuthManager,
    JWTPayload,
    RefreshRequest,
    TokenResponse,
    UserLoginRequest,
    UserProfile,
    UserRegisterRequest,
    UserResponse,
)

# ── Sentence ──────────────────────────────────────────────────────────
from shared_models.sentence import (
    SceneSegment,
    SentenceBlock,
    SplitResult,
    SubtitleBlock,
)

# ── Content ───────────────────────────────────────────────────────────
from shared_models.content import (
    ContentFetchRequest,
    RewriteConfig,
    RewriteResult,
)

# ── Prompt ────────────────────────────────────────────────────────────
from shared_models.prompt import (
    OptimizeRequest,
    OptimizeResult,
    ReverseRequest,
    ReverseResult,
)

# ── Pipeline (Week 0 核心契约) ──────────────────────────────────────
from shared_models.pipeline import (
    ContentPacket,
    PipelineStage,
    ScenePrompt,
    VideoAsset,
)

# ── LLM Config ───────────────────────────────────────────────────────────
from shared_models.llm import (
    LLMGlobalConfig,
    LLMInvocationRequest,
    LLMInvocationResponse,
    LLMProviderConfig,
    ModelRoute,
    UserLLMOverride,
)

# ── Viral Analysis ─────────────────────────────────────────────────────────
from shared_models.viral import (
    ArticleViralProfile,
    ContentStructure,
    EmotionalTrigger,
    EngagementMetrics,
    TitleAnalysis,
    TitleStructure,
    TrendingInsights,
    ViralAnalysisResult,
    ViralFactor,
    ViralScoringConfig,
)

# ── TrendScope ────────────────────────────────────────────────────────
from shared_models.trendscope.models import (
    HotArticleModel,
    PlatformModel,
    TrendingPipelineItem,
    TrendingTopicModel,
    TrendingListResponse,
)

__all__ = [
    # auth
    "JWTAuthManager",
    "JWTPayload",
    "RefreshRequest",
    "TokenResponse",
    "UserLoginRequest",
    "UserProfile",
    "UserRegisterRequest",
    "UserResponse",
    # sentence
    "SceneSegment",
    "SentenceBlock",
    "SplitResult",
    "SubtitleBlock",
    # content
    "ContentFetchRequest",
    "RewriteConfig",
    "RewriteResult",
    # prompt
    "OptimizeRequest",
    "OptimizeResult",
    "ReverseRequest",
    "ReverseResult",
    # pipeline (Week 0)
    "ContentPacket",
    "PipelineStage",
    "ScenePrompt",
    "VideoAsset",
    # trendscope
    "HotArticleModel",
    "PlatformModel",
    "TrendingPipelineItem",
    "TrendingTopicModel",
    "TrendingListResponse",
    # llm
    "LLMProviderConfig",
    "ModelRoute",
    "UserLLMOverride",
    "LLMInvocationRequest",
    "LLMInvocationResponse",
    "LLMGlobalConfig",
    # viral
    "ArticleViralProfile",
    "ContentStructure",
    "EmotionalTrigger",
    "EngagementMetrics",
    "TitleAnalysis",
    "TitleStructure",
    "TrendingInsights",
    "ViralAnalysisResult",
    "ViralFactor",
    "ViralScoringConfig",
]
