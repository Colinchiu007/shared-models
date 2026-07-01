// Module: pipeline -- Auto-generated from shared-models

export interface ContentPacket {
  /** Content UUID (pipe-global unique ID) */
  id: string;
  /** 当前管道阶段 */
  stage?: PipelineStage;
  /** 来源平台代号: baidu/weibo/douyin/… */
  source_platform: string;
  /** 原文链接 */
  source_url: string;
  /** 原标题 */
  source_title: string;
  /** 原始正文内容 */
  source_content: string;
  /** 热榜热度分（来自 trendscope） */
  source_hot_score?: number | unknown;
  /** 采集时间 */
  collected_at?: string;
  /** AI 改写标题 */
  rewritten_title?: string | unknown;
  /** AI 改写正文 */
  rewritten_content?: string | unknown;
  /** 改写风格 */
  rewrite_style?: string | unknown;
  /** 改写完成时间 */
  rewritten_at?: string | unknown;
  /** 分句结果 (SplitResult dict) */
  split_result?: Record<string, unknown> | unknown;
  /** 分句场景数 */
  total_scenes?: number | unknown;
  /** 估算时长(秒) */
  total_duration?: number | unknown;
  /** 分句完成时间 */
  split_at?: string | unknown;
  /** 场景级优化提示词列表 */
  optimized_prompts?: Array<Record<string, unknown>> | unknown;
  /** 提示词优化完成时间 */
  prompted_at?: string | unknown;
  /** 生成视频链接 */
  video_url?: string | unknown;
  /** 视频实际时长(秒) */
  video_duration?: number | unknown;
  /** 视频生成完成时间 */
  generated_at?: string | unknown;
  /** 多平台发布结果 {platform: url} */
  publish_results?: Record<string, unknown> | unknown;
  /** 发布完成时间 */
  published_at?: string | unknown;
  /** 失败原因 */
  error?: string | unknown;
  /** 标签列表 */
  tags?: Array<string>;
  /** 扩展元数据（各环节自由写入） */
  metadata?: Record<string, unknown>;
}

export type PipelineStage = "collected", "awaiting", "rewritten", "split", "prompted", "generated", "published", "failed";

export interface ScenePrompt {
  /** 场景序号 (0-based) */
  scene_id: number;
  /** 场景标题 */
  title?: string;
  /** 场景原文 */
  text: string;
  /** AI 生成的图片提示词 */
  prompt: string;
  /** 该场景字幕文本 */
  subtitle_text?: string;
  /** 场景时长(秒) */
  duration?: number;
  /** 涉及角色 */
  character?: string;
  /** 场景设定 */
  setting?: string;
  /** 场景情绪 */
  mood?: string;
}

export interface VideoAsset {
  /** Video asset UUID */
  id: string;
  /** 视频标题 */
  title: string;
  /** 场景列表（按顺序合成） */
  scenes: Array<ScenePrompt>;
  /** 视频风格 */
  style?: string;
  /** 目标平台（影响画幅/时长） */
  platform?: string;
  /** 背景音乐路径/URL */
  background_music?: string | unknown;
  /** 配音音色 */
  voice_type?: string;
  /** 是否生成字幕 */
  subtitle_enabled?: boolean;
  /** 视频分辨率 宽x高 */
  resolution?: string;
  /** 帧率 */
  fps?: number;
  /** 其他元数据 */
  metadata?: Record<string, unknown>;
}
