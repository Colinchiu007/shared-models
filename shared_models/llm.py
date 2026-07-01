"""Unified LLM configuration data models (Pydantic v2)

Bridges 4 existing LLM config implementations across the monorepo:

| System | Storage | Encryption | Environment |
|--------|---------|------------|-------------|
| platform-orchestrator/provider_router.py | SQLite (aiosqlite) | Fernet AES-GCM | PO_SECRET_KEY |
| platform-orchestrator/config.py | env vars (pydantic-settings) | None | PO_* env |
| prompt-engine/config.yaml | YAML file | None | Env var in YAML values |
| auto-exec-mechanism/model_routing.py | JSON file + DEFAULT_ROUTES | None | None |

This module defines the shared data contract only — each project retains its own
storage/persistence layer but uses these models for type safety and cross-project
interop.
"""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal, Optional


# ── Type Aliases ──────────────────────────────────────────────────────────

ProviderType = Literal[
    "openai_compat",   # OpenAI / OpenRouter / DeepSeek / Groq / etc.
    "xfyun",           # 讯飞星火 (Xfyun)
    "minimax",         # MiniMax
    "gemini",          # Google Gemini / Vertex AI
    "doubao",          # 豆包 / 字节跳动火山引擎
    "qwen",            # 通义千问 (Alibaba Cloud)
    "anthropic",       # Anthropic Claude (direct API)
]

CostLevel = Literal["low", "medium", "high"]
"""Relative cost tier for model routing decisions."""

RouteCategory = Literal[
    "ultrabrain",           # Deep reasoning / complex analysis
    "visual-engineering",   # Multi-modal / vision / engineering
    "deep",                 # Code / technical / architecture
    "creative",             # Writing / copy / design
    "quick",                # Fast / low-cost / simple
]
"""Task categories for model routing (from auto-exec-mechanism)."""


# ── Core Models ───────────────────────────────────────────────────────────


class LLMProviderConfig(BaseModel):
    """LLM provider configuration — unified data contract.

    How config is persisted varies by project:
    - **DB-backed** (platform-orchestrator): provider_configs table, Fernet encryption
    - **YAML** (prompt-engine): config.yaml with ${ENV_VAR} resolution
    - **JSON** (auto-exec-mechanism): model_routes.json overrides
    - **env** (platform-orchestrator/config.py): pydantic-settings BaseSettings

    This model is the *in-memory representation* shared across all persistence
    strategies. API key is in plaintext by design — encryption is the responsibility
    of the storage layer (see orchestrator's Fernet helpers).
    """

    name: str = Field(
        ...,
        description="Unique provider identifier, e.g. 'openai', 'doubao', 'minimax'",
        min_length=1,
    )
    provider_type: ProviderType = Field(
        ...,
        description="Provider protocol type — determines which SDK/client to use",
    )
    base_url: str = Field(
        default="",
        description="API endpoint base URL (empty = use SDK default)",
    )
    api_key: str = Field(
        default="",
        description="API key (plaintext in this model — encrypt at rest)",
    )
    display_name: str = Field(
        default="",
        description="Human-readable label for UI display",
    )

    # ── Model selection ──
    models: list[str] = Field(
        default_factory=list,
        description="All available model names for this provider",
    )
    default_model: str = Field(
        default="",
        description="Default model used when not explicitly specified",
    )

    # ── Request defaults ──
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, gt=0)
    timeout: int = Field(default=60, gt=0)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)

    # ── Routing & access ──
    priority: int = Field(
        default=0,
        description="Higher = preferred when multiple providers are equivalent",
    )
    min_tier: int = Field(
        default=1,
        description="Minimum user access tier (0 = admin, 1 = all, 2+ = premium)",
    )
    enabled: bool = Field(default=True)

    # ── Extensibility ──
    extra_config: dict = Field(
        default_factory=dict,
        description="Provider-specific overrides (e.g. organization_id, api_version)",
    )

    # ── Storage metadata ──
    id: Optional[str] = Field(
        default=None,
        description="DB record UUID (set by storage layer)",
    )
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ModelRoute(BaseModel):
    """Category-based model routing rule.

    Maps a semantic task category to a (provider, model) pair.
    Inspired by auto-exec-mechanism's routing table and oh-my-openagent patterns.

    Example:
        route = ModelRoute(
            category="creative",
            provider="openai",
            model="gpt-4o",
            fallback_model="gpt-4o-mini",
            keywords=["write", "draft", "copy", "写作", "文案"],
            description="Creative writing / copy / content generation",
            cost_level="medium",
        )
    """

    category: RouteCategory = Field(
        ...,
        description="Task classification category",
    )
    provider: str = Field(
        ...,
        description="Target provider name (refers to LLMProviderConfig.name)",
    )
    model: str = Field(
        ...,
        description="Target model to use for this category",
    )
    fallback_model: Optional[str] = Field(
        default=None,
        description="Fallback model when primary is unavailable",
    )

    # ── Classification hints ──
    keywords: list[str] = Field(
        default_factory=list,
        description="Keywords used by the classifier to auto-assign categories",
    )
    description: str = Field(
        default="",
        description="Human-readable description of what this category handles",
    )

    # ── Economics ──
    cost_level: CostLevel = Field(default="medium")
    priority: int = Field(default=0)

    # ── Usage ──
    usage_count: int = Field(default=0, description="How many times this route was hit")
    last_used_at: Optional[datetime] = None


class UserLLMOverride(BaseModel):
    """Per-user provider override.

    Allows individual users to supply their own API keys instead of using the
    admin-configured shared key. This is the data contract for the orchestrator's
    user_api_keys table.

    When a user override exists, the system uses the user's key + optional base_url
    instead of the admin config for that provider.
    """

    user_uuid: str = Field(..., description="User who owns this override")
    provider_name: str = Field(
        ...,
        description="Provider to override (matches LLMProviderConfig.name)",
    )
    api_key: str = Field(
        ...,
        description="User's own API key (plaintext — encrypt at rest)",
    )
    base_url: Optional[str] = Field(
        default=None,
        description="Optional custom endpoint override for this user",
    )
    model: Optional[str] = Field(
        default=None,
        description="Optional model restriction for this user",
    )
    is_active: bool = Field(default=True)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ── Runtime models ────────────────────────────────────────────────────────


class LLMInvocationRequest(BaseModel):
    """Standardized LLM invocation request.

    Used across prompt-engine, orchestrator, and any service that needs to call an LLM.
    Replaces each project's ad-hoc request format with a shared contract.

    The request can be resolved in two ways:
    1. **Direct**: specify ``provider`` + ``model`` explicitly
    2. **Routed**: specify ``category`` + optional ``user_uuid``, let the router decide
    """

    messages: list[dict] = Field(
        ...,
        description="Chat messages in OpenAI format: [{'role': 'user', 'content': ...}]",
    )
    system_prompt: Optional[str] = Field(
        default=None,
        description="Optional system message prepended to messages",
    )

    # ── Direct resolution ──
    provider: Optional[str] = Field(
        default=None,
        description="Target provider (matches LLMProviderConfig.name)",
    )
    model: Optional[str] = Field(
        default=None,
        description="Target model name",
    )

    # ── Parameter overrides ──
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, gt=0)
    top_p: Optional[float] = Field(default=None, ge=0.0, le=1.0)

    # ── Route-based resolution ──
    user_uuid: Optional[str] = Field(
        default=None,
        description="For user-level API key override",
    )
    category: Optional[RouteCategory] = Field(
        default=None,
        description="Route category for auto-selection (mutually exclusive with provider)",
    )
    min_tier: int = Field(default=1, description="Caller's access tier for routing")

    # ── Streaming ──
    stream: bool = Field(default=False)
    stream_callback_url: Optional[str] = Field(
        default=None,
        description="POST callback URL for streaming chunks",
    )


class LLMInvocationResponse(BaseModel):
    """Standardized LLM invocation response."""

    content: str = Field(..., description="Generated text content")

    # ── Identity ──
    model: str = Field(default="", description="Model that generated the response")
    provider: str = Field(default="", description="Provider that served the request")
    finish_reason: str = Field(default="stop", description="stop / length / content_filter / error")

    # ── Usage ──
    input_tokens: int = Field(default=0)
    output_tokens: int = Field(default=0)
    total_tokens: int = Field(default=0)

    # ── Performance ──
    latency_ms: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now().astimezone())


# ── Aggregated config ─────────────────────────────────────────────────────


class LLMGlobalConfig(BaseModel):
    """Complete LLM configuration for a project/service.

    Aggregates provider definitions, routing rules, and defaults into one object.
    This is the top-level config that projects like platform-orchestrator can
    construct from their storage layer and pass to consumers.

    Example YAML-equivalent:
        providers:
          - name: openai
            provider_type: openai_compat
            base_url: https://api.openai.com/v1
            models: [gpt-4o, gpt-4o-mini]
            default_model: gpt-4o
          - name: doubao
            provider_type: doubao
            ...

        routing:
          quick:
            provider: openai
            model: gpt-4o-mini
            cost_level: low
          deep:
            provider: openai
            model: gpt-4o
            cost_level: medium

        defaults:
          temperature: 0.7
          max_tokens: 4096
          timeout: 60
    """

    providers: list[LLMProviderConfig] = Field(default_factory=list)
    routing: list[ModelRoute] = Field(default_factory=list)
    user_overrides: list[UserLLMOverride] = Field(default_factory=list)

    # ── System-wide defaults ──
    default_temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    default_max_tokens: int = Field(default=4096, gt=0)
    default_timeout: int = Field(default=60, gt=0)
    default_provider: str = Field(default="", description="Fallback provider if routing fails")

    # ── Lookup helpers ──

    def get_provider(self, name: str) -> Optional[LLMProviderConfig]:
        """Lookup a provider config by name."""
        for p in self.providers:
            if p.name == name:
                return p
        return None

    def get_route(self, category: str) -> Optional[ModelRoute]:
        """Lookup a routing rule by category."""
        for r in self.routing:
            if r.category == category:
                return r
        return None

    def get_user_override(self, user_uuid: str, provider_name: str) -> Optional[UserLLMOverride]:
        """Get active user override for a provider."""
        for o in self.user_overrides:
            if o.user_uuid == user_uuid and o.provider_name == provider_name and o.is_active:
                return o
        return None
