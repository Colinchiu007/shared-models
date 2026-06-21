"""shared-models: Pydantic v2 data contracts for the platform-orchestrator pipeline.

Models are organized by domain:
- splitter: SentenceBlock, SceneSegment, SubtitleBlock, EraInfo, SplitResult
- prompt: PlatformType, StyleType, OptimizeRequest, OptimizeResult
- article: ArticleCreate, ArticleResponse, RewriteRequest, CollectResponse
- auth: UserRegisterRequest, TokenResponse, UserProfile
- pipeline: PipelineJob, VideoJob, PipelineStatus, VideoJobStatus
- publish: PublishTask, PublishResult, PlatformAccount

All models use Pydantic v2 with extra="allow" for forward compatibility.
"""

from shared_models.__about__ import __version__

# ── Splitter ────────────────────────────────────────────────────────────────
from shared_models.splitter import (
    EraInfo,
    SceneSegment,
    SentenceBlock,
    SplitResult,
    SubtitleBlock,
)

# ── Prompt Engine ────────────────────────────────────────────────────────────
from shared_models.prompt import (
    OptimizeRequest,
    OptimizeResult,
    PlatformType,
    ReverseRequest,
    ReverseResult,
    StyleCategory,
    StyleCategoryResult,
    StyleType,
)

# ── Article / Content ───────────────────────────────────────────────────────
from shared_models.article import (
    ArticleCreate,
    ArticleListItem,
    ArticleResponse,
    CollectResponse,
    CollectURLRequest,
    RewriteRequest,
)

# ── Auth / User ─────────────────────────────────────────────────────────────
from shared_models.auth import (
    RefreshRequest,
    TokenResponse,
    UserLoginRequest,
    UserProfile,
    UserRegisterRequest,
    UserResponse,
)

# ── Pipeline / Video ────────────────────────────────────────────────────────
from shared_models.pipeline import (
    PipelineJob,
    PipelineStatus,
    VideoJob,
    VideoJobStatus,
)

# ── Publish ─────────────────────────────────────────────────────────────────
from shared_models.publish import (
    PlatformAccount,
    PublishPlatformType,
    PublishResult,
    PublishTask,
    PublishTaskStatus,
)

__all__ = [
    "__version__",
    # Splitter
    "SentenceBlock",
    "EraInfo",
    "SubtitleBlock",
    "SceneSegment",
    "SplitResult",
    # Prompt
    "PlatformType",
    "StyleType",
    "StyleCategory",
    "StyleCategoryResult",
    "OptimizeRequest",
    "OptimizeResult",
    "ReverseRequest",
    "ReverseResult",
    # Article
    "ArticleCreate",
    "ArticleListItem",
    "ArticleResponse",
    "CollectURLRequest",
    "CollectResponse",
    "RewriteRequest",
    # Auth
    "UserRegisterRequest",
    "UserLoginRequest",
    "RefreshRequest",
    "UserResponse",
    "TokenResponse",
    "UserProfile",
    # Pipeline
    "PipelineStatus",
    "PipelineJob",
    "VideoJobStatus",
    "VideoJob",
    # Publish
    "PublishPlatformType",
    "PublishTaskStatus",
    "PublishResult",
    "PublishTask",
    "PlatformAccount",
]
