// Module: trendscope -- Auto-generated from shared-models

export interface HotArticleModel {
  id?: number | unknown;
  /** Nested platform {code, name, icon_url} */
  platform?: Record<string, unknown>;
  title?: string;
  summary?: string;
  content_text?: string | unknown;
  images?: Array<Record<string, unknown>>;
  video_url?: string;
  source_url?: string;
  author_name?: string;
  author_avatar?: string;
  read_count?: number;
  like_count?: number;
  comment_count?: number;
  share_count?: number;
  favor_count?: number;
  collected_count?: number;
  author_followers?: number;
  viral_score?: number;
  viral_score_norm?: number;
  publish_at?: string;
  snapshot_at?: string;
}

export interface PlatformModel {
  id: number;
  code: string;
  name: string;
  icon_url?: string;
  category?: string;
  is_active?: boolean;
}

export interface TrendingListResponse {
  items: Array<TrendingTopicModel>;
  total: number;
  page?: number;
  page_size?: number;
}

export interface TrendingTopicModel {
  id?: number | unknown;
  /** Nested platform {code, name, icon_url} */
  platform?: Record<string, unknown>;
  rank: number;
  title: string;
  hot_value: string;
  hot_value_norm?: number;
  topic_url?: string;
  category?: string;
  snapshot_at?: string;
}

export interface TrendingPipelineItem {
  source_url: string;
  title: string;
  /** Nested platform {code, name} */
  platform?: Record<string, unknown>;
  summary?: string;
  author_name?: string;
  read_count?: number;
  like_count?: number;
}
