"""shared-models: Unified Pydantic v2 data contracts

All modules in the one-stop video generation platform import from this package
to ensure consistent data structures across process boundaries.
"""

# ── Auth ──────────────────────────────────────────────────────────────
from shared_models.auth import (
    JWTPayload,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
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
    "JWTPayload",
    "TokenResponse",
    "UserLoginRequest",
    "UserRegisterRequest",
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
    # trendscope
    "HotArticleModel",
    "PlatformModel",
    "TrendingPipelineItem",
    "TrendingTopicModel",
    "TrendingListResponse",
]
