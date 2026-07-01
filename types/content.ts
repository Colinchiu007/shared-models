// Module: content -- Auto-generated from shared-models

export interface CollectRequest {
  /** Source URL to fetch */
  url: string;
  /** Source identifier (manual/trendscope/rpa) */
  source?: string;
  /** Platform code if from trendscope */
  platform?: string | unknown;
}

export interface CollectResult {
  /** Collected article title */
  title?: string;
  /** Collected article content (plain text) */
  content?: string;
  /** Original source URL */
  source_url: string;
  /** Original author name */
  author?: string | unknown;
  /** Word count of collected content */
  word_count?: number;
}

export interface RewriteRequest {
  /** Source content to rewrite */
  content: string;
  /** Original title */
  title?: string;
  /** Rewrite style: casual / formal / eye-catching / deep-analysis */
  style?: string;
  /** Length strategy: keep / compress / expand / short / medium / long */
  length?: string;
  /** Target platform for style tuning */
  target_platform?: string | unknown;
  /** Enable SEO optimization */
  seo_optimize?: boolean;
}

export interface RewriteResult {
  /** AI-optimized title */
  rewritten_title?: string;
  /** Rewritten content */
  rewritten_content: string;
  /** Applied rewrite style */
  style?: string;
  /** Word count of rewritten content */
  word_count?: number;
  /** LLM model used */
  model_used?: string;
  created_at?: string;
}
