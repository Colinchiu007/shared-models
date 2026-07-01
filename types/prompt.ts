// Module: prompt -- Auto-generated from shared-models

export interface BatchOptimizeRequest {
  /** 优化请求列表 */
  requests: Array<OptimizeRequest>;
}

export interface OptimizeRequest {
  /** 原始提示词 */
  prompt: string;
  /** 目标平台: Midjourney / Stable Diffusion / DALL·E / 通义万相 / 文心一格 / 即梦 / 通用 */
  platform?: string;
  /** 艺术风格 */
  style?: string | unknown;
  /** 创意程度 1-10 */
  creative_level?: number;
  /** 优化结果最大字符数 */
  max_length?: number;
  /** 负面提示词 */
  negative_prompt?: string | unknown;
  /** 候选版本数量 */
  num_candidates?: number;
  /** 当 style=None 时是否自动检测风格 */
  auto_detect_style?: boolean;
  /** 外部注入上下文: synopsis, character, setting 等 */
  context?: Record<string, unknown> | unknown;
}

export interface OptimizeResult {
  /** 优化后的提示词 */
  optimized_prompt: string;
  /** 实际使用的平台策略 */
  platform: string;
  /** 使用的风格 */
  style?: string | unknown;
  /** LLM 模型名称 */
  model_used?: string;
  /** 消耗的 token 数 */
  tokens_used?: number;
  /** 优化耗时（毫秒） */
  duration_ms?: number;
  /** 多候选版本 */
  candidates?: Array<string>;
  /** 错误信息 */
  error?: string | unknown;
}

export interface ReverseRequest {
  /** 图片 URL */
  image_url: string;
  /** 目标平台 */
  platform?: string;
  /** 艺术风格 */
  style?: string | unknown;
  /** 分析详细度: low / auto / high */
  detail?: string;
}

export interface ReverseResult {
  /** 图片 URL */
  image_url: string;
  /** 生成的提示词 */
  prompt: string;
  /** 目标平台 */
  platform: string;
  /** 艺术风格 */
  style?: string | unknown;
  /** LLM 模型名称 */
  model_used?: string;
  /** 图片描述（纯文本） */
  description?: string;
  /** 耗时 */
  duration_ms?: number;
  /** 错误信息 */
  error?: string | unknown;
  /** 置信度 */
  confidence?: number;
}

export interface RewriteRequest {
  /** 原始简短描述 */
  prompt: string;
  /** 目标平台 */
  platform?: string;
  /** 输出最大字符数 */
  max_length?: number;
}
