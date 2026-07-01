// Module: viral -- Auto-generated from shared-models

export interface ArticleViralProfile {
  platform_code?: string;
  title?: string;
  author_name?: string;
  author_followers?: number;
  source_url?: string;
  category?: string;
  title_analysis?: TitleAnalysis;
  engagement?: EngagementMetrics;
  factors?: Array<ViralFactor>;
  overall_score?: number;
  rank?: number;
  snapshot_at?: string | unknown;
}

export type EmotionalTrigger = "curiosity", "surprise", "controversy", "empathy", "anxiety", "fear", "joy", "anger", "inspiration", "none";

export interface EngagementMetrics {
  likes?: number;
  comments?: number;
  shares?: number;
  favorites?: number;
  views?: number;
  likes_norm?: number;
  comments_norm?: number;
  shares_norm?: number;
  favorites_norm?: number;
  total_engagement?: number;
  engagement_rate?: number;
  viral_score?: number;
}

export interface TitleAnalysis {
  /** Original title text */
  title: string;
  structure?: TitleStructure;
  /** Character count */
  length?: number;
  word_count?: number;
  has_numbers?: boolean;
  has_questions?: boolean;
  has_emojis?: boolean;
  has_colon?: boolean;
  has_power_words?: Array<string>;
  emotion?: EmotionalTrigger;
  confidence?: number;
}

export type TitleStructure = "question", "numbered_list", "how_to", "comparison", "suspense", "direct", "controversy", "story", "negative", "command", "curiosity_gap", "timely", "other";

export interface ViralFactor {
  /** Factor name, e.g. 'title_structure', 'emotion' */
  name: string;
  /** Human-readable label in Chinese */
  label?: string;
  /** Normalized score 0-1 */
  score?: number;
  /** Detection confidence */
  confidence?: number;
  /** Supporting evidence snippets */
  evidence?: Array<string>;
  /** Extra factor-specific data */
  details?: Record<string, unknown>;
}

export type ContentStructure = "list", "story", "tutorial", "opinion", "emotional", "news", "review", "guide", "other";

export interface TrendingInsights {
  platform_code?: string;
  snapshot_at?: string;
  total_items?: number;
  category_distribution?: Record<string, number>;
  title_structure_distribution?: Record<string, number>;
  emotion_distribution?: Record<string, number>;
  top_topics?: Array<Record<string, unknown>>;
  rising_keywords?: Array<Record<string, unknown>>;
}

export interface ViralAnalysisResult {
  /** Analyzed topic or keyword */
  topic: string;
  analyzed_at?: string;
  overall_score?: number;
  trend_direction?: string;
  confidence?: number;
  factors?: Array<ViralFactor>;
  articles?: Array<ArticleViralProfile>;
  platform_scores?: Record<string, number>;
  /** Recommended title structures with expected lift */
  suggested_structures?: Array<Record<string, unknown>>;
  /** Alternative writing angles for this topic */
  suggested_angles?: Array<string>;
}

export interface ViralScoringConfig {
  weight_likes?: number;
  weight_comments?: number;
  weight_shares?: number;
  weight_favorites?: number;
  w_linear?: number;
  w_log?: number;
  w_authority?: number;
  /** Max raw value for normalization */
  norm_ceiling?: number;
  log_base?: number;
  platform_ceilings?: Record<string, Array<number>>;
}
