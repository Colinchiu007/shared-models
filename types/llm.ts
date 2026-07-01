// Module: llm -- Auto-generated from shared-models

export interface LLMGlobalConfig {
  providers?: Array<LLMProviderConfig>;
  routing?: Array<ModelRoute>;
  user_overrides?: Array<UserLLMOverride>;
  default_temperature?: number;
  default_max_tokens?: number;
  default_timeout?: number;
  /** Fallback provider if routing fails */
  default_provider?: string;
}

export interface LLMProviderConfig {
  /** Unique provider identifier, e.g. 'openai', 'doubao', 'minimax' */
  name: string;
  /** Provider protocol type — determines which SDK/client to use */
  provider_type: ("openai_compat", "xfyun", "minimax", "gemini", "doubao", "qwen", "anthropic");
  /** API endpoint base URL (empty = use SDK default) */
  base_url?: string;
  /** API key (plaintext in this model — encrypt at rest) */
  api_key?: string;
  /** Human-readable label for UI display */
  display_name?: string;
  /** All available model names for this provider */
  models?: Array<string>;
  /** Default model used when not explicitly specified */
  default_model?: string;
  temperature?: number;
  max_tokens?: number;
  timeout?: number;
  top_p?: number;
  /** Higher = preferred when multiple providers are equivalent */
  priority?: number;
  /** Minimum user access tier (0 = admin, 1 = all, 2+ = premium) */
  min_tier?: number;
  enabled?: boolean;
  /** Provider-specific overrides (e.g. organization_id, api_version) */
  extra_config?: Record<string, unknown>;
  /** DB record UUID (set by storage layer) */
  id?: string | unknown;
  created_at?: string | unknown;
  updated_at?: string | unknown;
}

export interface ModelRoute {
  /** Task classification category */
  category: ("ultrabrain", "visual-engineering", "deep", "creative", "quick");
  /** Target provider name (refers to LLMProviderConfig.name) */
  provider: string;
  /** Target model to use for this category */
  model: string;
  /** Fallback model when primary is unavailable */
  fallback_model?: string | unknown;
  /** Keywords used by the classifier to auto-assign categories */
  keywords?: Array<string>;
  /** Human-readable description of what this category handles */
  description?: string;
  cost_level?: ("low", "medium", "high");
  priority?: number;
  /** How many times this route was hit */
  usage_count?: number;
  last_used_at?: string | unknown;
}

export interface UserLLMOverride {
  /** User who owns this override */
  user_uuid: string;
  /** Provider to override (matches LLMProviderConfig.name) */
  provider_name: string;
  /** User's own API key (plaintext — encrypt at rest) */
  api_key: string;
  /** Optional custom endpoint override for this user */
  base_url?: string | unknown;
  /** Optional model restriction for this user */
  model?: string | unknown;
  is_active?: boolean;
  created_at?: string | unknown;
  updated_at?: string | unknown;
}

export interface LLMInvocationRequest {
  /** Chat messages in OpenAI format: [{'role': 'user', 'content': ...}] */
  messages: Array<Record<string, unknown>>;
  /** Optional system message prepended to messages */
  system_prompt?: string | unknown;
  /** Target provider (matches LLMProviderConfig.name) */
  provider?: string | unknown;
  /** Target model name */
  model?: string | unknown;
  temperature?: number | unknown;
  max_tokens?: number | unknown;
  top_p?: number | unknown;
  /** For user-level API key override */
  user_uuid?: string | unknown;
  /** Route category for auto-selection (mutually exclusive with provider) */
  category?: ("ultrabrain", "visual-engineering", "deep", "creative", "quick") | unknown;
  /** Caller's access tier for routing */
  min_tier?: number;
  stream?: boolean;
  /** POST callback URL for streaming chunks */
  stream_callback_url?: string | unknown;
}

export interface LLMInvocationResponse {
  /** Generated text content */
  content: string;
  /** Model that generated the response */
  model?: string;
  /** Provider that served the request */
  provider?: string;
  /** stop / length / content_filter / error */
  finish_reason?: string;
  input_tokens?: number;
  output_tokens?: number;
  total_tokens?: number;
  latency_ms?: number;
  created_at?: string;
}
