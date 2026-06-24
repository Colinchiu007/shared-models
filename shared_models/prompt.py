"""Prompt optimization engine data models"""
from pydantic import BaseModel, Field


class OptimizeRequest(BaseModel):
    raw_prompt: str = Field(..., min_length=1)
    target_platform: str = "通用"  # Midjourney、Stable Diffusion、DALL·E、通义万相、文心一格、即梦、通用
    language: str = "zh"
    style: str | None = None
    num_candidates: int = 1


class OptimizeResult(BaseModel):
    raw_prompt: str
    optimized_prompt: str
    platform: str
    style: str | None = None
    tokens_used: int = 0


class ReverseRequest(BaseModel):
    image_url: str = Field(..., description="URL of the image to reverse-engineer")
    target_platform: str = "通用"


class ReverseResult(BaseModel):
    image_url: str
    guessed_prompt: str
    platform: str
    confidence: float = 0.0
