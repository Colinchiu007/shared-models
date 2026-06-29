"""Prompt optimization engine data models — Pipeline Contract v1

Canonical data contracts for the prompt optimization pipeline.
All prompt-engine modules import from here; domain-specific extensions
live in prompt_engine.models.
"""
from typing import Optional
from pydantic import BaseModel, Field


class OptimizeRequest(BaseModel):
    """提示词优化请求（管道契约）"""
    prompt: str = Field(..., min_length=1, max_length=2000, description="原始提示词")
    platform: str = Field(default="通用", description="目标平台: Midjourney / Stable Diffusion / DALL·E / 通义万相 / 文心一格 / 即梦 / 通用")
    style: Optional[str] = Field(default=None, description="艺术风格")
    creative_level: int = Field(default=5, ge=1, le=10, description="创意程度 1-10")
    max_length: int = Field(default=300, ge=50, le=2000, description="优化结果最大字符数")
    negative_prompt: Optional[str] = Field(default=None, max_length=500, description="负面提示词")
    num_candidates: int = Field(default=1, ge=1, le=5, description="候选版本数量")
    auto_detect_style: bool = Field(default=True, description="当 style=None 时是否自动检测风格")
    context: Optional[dict] = Field(default=None, description="外部注入上下文: synopsis, character, setting 等")


class OptimizeResult(BaseModel):
    """提示词优化结果（管道契约）"""
    optimized_prompt: str = Field(..., description="优化后的提示词")
    platform: str = Field(..., description="实际使用的平台策略")
    style: Optional[str] = Field(default=None, description="使用的风格")
    model_used: str = Field(default="", description="LLM 模型名称")
    tokens_used: int = Field(default=0, description="消耗的 token 数")
    duration_ms: float = Field(default=0.0, description="优化耗时（毫秒）")
    candidates: list[str] = Field(default_factory=list, description="多候选版本")
    error: Optional[str] = Field(default=None, description="错误信息")


class ReverseRequest(BaseModel):
    """图片逆向工程请求（管道契约）"""
    image_url: str = Field(..., description="图片 URL")
    platform: str = Field(default="通用", description="目标平台")
    style: Optional[str] = Field(default=None, description="艺术风格")
    detail: str = Field(default="auto", description="分析详细度: low / auto / high")


class ReverseResult(BaseModel):
    """逆向工程结果（管道契约）"""
    image_url: str = Field(..., description="图片 URL")
    prompt: str = Field(..., description="生成的提示词")
    platform: str = Field(..., description="目标平台")
    style: Optional[str] = Field(default=None, description="艺术风格")
    model_used: str = Field(default="", description="LLM 模型名称")
    description: str = Field(default="", description="图片描述（纯文本）")
    duration_ms: float = Field(default=0.0, description="耗时")
    error: Optional[str] = Field(default=None, description="错误信息")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="置信度")


class BatchOptimizeRequest(BaseModel):
    """批量优化请求"""
    requests: list[OptimizeRequest] = Field(..., min_length=1, max_length=10, description="优化请求列表")


class RewriteRequest(BaseModel):
    """Prompt 扩写请求"""
    prompt: str = Field(..., min_length=1, max_length=500, description="原始简短描述")
    platform: str = Field(default="通用", description="目标平台")
    max_length: int = Field(default=500, ge=50, le=2000, description="输出最大字符数")
