"""Pipeline state machine and video job models.

Defines the orchestration layer's job tracking models:
- PipelineStatus → Generic pipeline states
- PipelineJob → Generic job entity with input/output
- VideoJobStatus → Video-specific states
- VideoJob → Video generation job tracking
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PipelineStatus(str, Enum):
    """Generic pipeline job status."""

    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class PipelineJob(BaseModel):
    """Generic pipeline job for tracking any module's async task."""

    id: str = Field(..., description="Job ID (UUID)")
    status: PipelineStatus = Field(default=PipelineStatus.PENDING, description="Current status")
    user_id: Optional[str] = Field(default=None, description="Owner user ID")
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Input payload")
    output_data: Dict[str, Any] = Field(default_factory=dict, description="Output payload")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")

    model_config = {"extra": "allow"}


class VideoJobStatus(str, Enum):
    """Video generation job status — granular states for progress tracking."""

    QUEUED = "queued"
    GENERATING_AUDIO = "generating_audio"
    GENERATING_IMAGES = "generating_images"
    COMPOSITING = "compositing"
    DONE = "done"
    FAILED = "failed"


class VideoJob(BaseModel):
    """Video generation job — tracks the full Story2Video pipeline."""

    id: str = Field(..., description="Job ID (UUID)")
    status: VideoJobStatus = Field(
        default=VideoJobStatus.QUEUED, description="Current processing stage"
    )
    title: str = Field(default="", description="Video title")
    scenes: List[Dict[str, Any]] = Field(
        default_factory=list, description="Scene blocks with optimized prompts"
    )
    output_path: Optional[str] = Field(default=None, description="Output video file path")
    progress: float = Field(default=0.0, ge=0.0, le=1.0, description="Progress 0-1")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    created_at: Optional[datetime] = Field(default=None, description="Job creation time")
    completed_at: Optional[datetime] = Field(default=None, description="Job completion time")

    model_config = {"extra": "allow"}
