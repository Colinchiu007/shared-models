// Module: sentence -- Auto-generated from shared-models

export interface EraInfo {
  /** 时代标签: modern / ancient / mixed */
  era: string;
  /** 置信度 0-1 */
  confidence: number;
  /** 匹配到的关键词列表 */
  keywords?: Array<string>;
}

export interface SceneSegment {
  text: string;
  segment_id: number;
  estimated_duration: number;
  target_words: number;
  sentences?: Array<SentenceBlock>;
  era_info?: EraInfo | unknown;
  subtitles?: Array<SubtitleBlock>;
  characters?: Array<string>;
  setting?: string;
  mood?: string;
  story_phase?: string;
}

export interface SentenceBlock {
  text: string;
  index: number;
  char_count?: number;
  word_count?: number;
  words?: Array<string>;
  pos_tags?: Array<string>;
  language?: string;
  tier?: string;
  confidence?: number;
  is_topic_boundary?: boolean;
  topic_depth_score?: number;
  length_status?: string;
  length_strategy_applied?: string;
}

export interface SubtitleBlock {
  text: string;
  display_order: number;
  start_time: number;
  duration: number;
  parent_segment_id: number;
}

export interface SplitResult {
  sentences?: Array<SentenceBlock>;
  scenes?: Array<SceneSegment>;
  tier_used?: string;
  language?: string;
  total_duration?: number;
  total_words?: number;
  total_scenes?: number;
  config_snapshot?: Record<string, unknown>;
  script_analysis?: Record<string, unknown> | unknown;
}
