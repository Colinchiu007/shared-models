"""Pipeline core data contracts — frozen at Week 0 Interface Freeze.

ContentPacket:  数据管道通用容器 (A→B→C)
VideoAsset:     视频合成任务输入规格 (prompt-engine→Story2Video)

冻结日期: 2026-06-25
版本: v0.1.0
变更流程: 需三组全部 ACK + 协调者批准
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ── Pipeline Stages & Status ──────────────────────────────────────────────


class PipelineStage(str, Enum):
    """管道生命周期阶段。"""

    COLLECTED = "collected"           # 刚采集（原始数据，来自 trendscope）
    PIPELINE_AWAITING = "awaiting"    # 排队等待改写/发布（已写入 DB）
    REWRITTEN = "rewritten"           # AI 改写完成（来自 content-aggregator）
    SPLIT = "split"                   # 语义分句完成（来自 smart-sentence-splitter）
    PROMPTED = "prompted"             # 提示词优化完成（来自 prompt-engine）
    GENERATED = "generated"           # 视频生成完成（来自 Story2Video）
    PUBLISHED = "published"           # 发布完成（来自 Multi-Publish）
    FAILED = "failed"                 # 管道中任一环节失败


# ── ContentPacket ──────────────────────────────────────────────────────────


class ContentPacket(BaseModel):
    """数据管道通用容器，携带内容从采集到发布的完整上下文。

    这是管道中最核心的数据契约。每个环节读取 input_data，写入 result_data，
    然后推进 stage。

    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ COLLECTED│───→│ REWRITTEN│───→│  SPLIT   │───→│ PROMPTED │───→│ GENERATED│
    │ trendscope│   │aggregator│   │ splitter │   │prompt-eng│   │Story2Video│
    └──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
    """

    id: str = Field(..., description="Content UUID (pipe-global unique ID)")
    stage: PipelineStage = Field(
        default=PipelineStage.COLLECTED, description="当前管道阶段"
    )

    # ── 来源信息（写一次，不再变更）──
    source_platform: str = Field(..., description="来源平台代号: baidu/weibo/douyin/…")
    source_url: str = Field(..., description="原文链接")
    source_title: str = Field(..., description="原标题")
    source_content: str = Field(..., description="原始正文内容")
    source_hot_score: Optional[float] = Field(
        default=None, description="热榜热度分（来自 trendscope）"
    )
    collected_at: datetime = Field(
        default_factory=datetime.now, description="采集时间"
    )

    # ── 改写结果（content-aggregator 写入）──
    rewritten_title: Optional[str] = Field(default=None, description="AI 改写标题")
    rewritten_content: Optional[str] = Field(default=None, description="AI 改写正文")
    rewrite_style: Optional[str] = Field(default=None, description="改写风格")
    rewritten_at: Optional[datetime] = Field(default=None, description="改写完成时间")

    # ── 分句结果（smart-sentence-splitter 写入）──
    split_result: Optional[Dict[str, Any]] = Field(
        default=None, description="分句结果 (SplitResult dict)"
    )
    total_scenes: Optional[int] = Field(default=None, description="分句场景数")
    total_duration: Optional[float] = Field(default=None, description="估算时长(秒)")
    split_at: Optional[datetime] = Field(default=None, description="分句完成时间")

    # ── 提示词结果（prompt-engine 写入）──
    optimized_prompts: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="场景级优化提示词列表"
    )
    prompted_at: Optional[datetime] = Field(default=None, description="提示词优化完成时间")

    # ── 视频结果（Story2Video 写入）──
    video_url: Optional[str] = Field(default=None, description="生成视频链接")
    video_duration: Optional[float] = Field(default=None, description="视频实际时长(秒)")
    generated_at: Optional[datetime] = Field(default=None, description="视频生成完成时间")

    # ── 发布结果（Multi-Publish 写入）──
    publish_results: Optional[Dict[str, Any]] = Field(
        default=None, description="多平台发布结果 {platform: url}"
    )
    published_at: Optional[datetime] = Field(default=None, description="发布完成时间")

    # ── 通用 ──
    error: Optional[str] = Field(default=None, description="失败原因")
    tags: List[str] = Field(default_factory=list, description="标签列表")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="扩展元数据（各环节自由写入）"
    )

    model_config = {"extra": "allow"}


# ── VideoAsset ─────────────────────────────────────────────────────────────


class ScenePrompt(BaseModel):
    """单场景的提示词与字幕配置。"""

    scene_id: int = Field(..., ge=0, description="场景序号 (0-based)")
    title: str = Field(default="", description="场景标题")
    text: str = Field(..., min_length=1, description="场景原文")
    prompt: str = Field(..., min_length=1, description="AI 生成的图片提示词")
    subtitle_text: str = Field(default="", description="该场景字幕文本")
    duration: float = Field(default=5.0, gt=0, description="场景时长(秒)")
    character: str = Field(default="", description="涉及角色")
    setting: str = Field(default="", description="场景设定")
    mood: str = Field(default="", description="场景情绪")

    model_config = {"extra": "allow"}


class VideoAsset(BaseModel):
    """视频合成任务输入规格 — 作为 Story2Video 的输入契约。

    区别于 VideoJob（任务追踪），VideoAsset 只描述"要生成什么"，
    不包含任务状态/进度等运行时信息。
    """

    id: str = Field(..., description="Video asset UUID")
    title: str = Field(..., min_length=1, description="视频标题")
    scenes: List[ScenePrompt] = Field(
        ..., min_length=1, description="场景列表（按顺序合成）"
    )
    style: str = Field(default="写实", description="视频风格")
    platform: str = Field(default="抖音", description="目标平台（影响画幅/时长）")
    background_music: Optional[str] = Field(default=None, description="背景音乐路径/URL")
    voice_type: str = Field(default="标准女声", description="配音音色")
    subtitle_enabled: bool = Field(default=True, description="是否生成字幕")
    resolution: str = Field(default="1080x1920", description="视频分辨率 宽x高")
    fps: int = Field(default=30, ge=24, le=60, description="帧率")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="其他元数据"
    )

    model_config = {"extra": "allow"}
