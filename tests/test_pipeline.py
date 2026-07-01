"""Tests for shared_models.pipeline — PipelineStage, ContentPacket, ScenePrompt, VideoAsset"""
import pytest
from datetime import datetime
from shared_models.pipeline import (
    ContentPacket,
    PipelineStage,
    ScenePrompt,
    VideoAsset,
)


class TestPipelineStage:
    """PipelineStage enum"""

    def test_values(self):
        assert PipelineStage.COLLECTED.value == "collected"
        assert PipelineStage.REWRITTEN.value == "rewritten"
        assert PipelineStage.SPLIT.value == "split"
        assert PipelineStage.PROMPTED.value == "prompted"
        assert PipelineStage.GENERATED.value == "generated"
        assert PipelineStage.PUBLISHED.value == "published"
        assert PipelineStage.FAILED.value == "failed"
        assert PipelineStage.PIPELINE_AWAITING.value == "awaiting"

    def test_all_members(self):
        assert len(PipelineStage) == 8

    def test_comparison(self):
        assert PipelineStage.COLLECTED != PipelineStage.REWRITTEN


class TestContentPacket:
    """ContentPacket — core pipeline data contract"""

    def test_minimal(self):
        packet = ContentPacket(
            id="pkt-001",
            source_platform="baidu",
            source_url="https://example.com",
            source_title="Test Article",
            source_content="This is the article content.",
        )
        assert packet.id == "pkt-001"
        assert packet.stage == PipelineStage.COLLECTED
        assert packet.source_platform == "baidu"
        assert packet.tags == []
        assert packet.metadata == {}

    def test_with_hot_score(self):
        packet = ContentPacket(
            id="pkt-002",
            source_platform="weibo",
            source_url="https://weibo.com/123",
            source_title="Hot Topic",
            source_content="Content",
            source_hot_score=95.5,
        )
        assert packet.source_hot_score == 95.5

    def test_rewritten_stage(self):
        packet = ContentPacket(
            id="pkt-003",
            source_platform="douyin",
            source_url="https://douyin.com/v/123",
            source_title="Original",
            source_content="Original content",
            stage=PipelineStage.REWRITTEN,
            rewritten_title="Rewritten Title",
            rewritten_content="Rewritten content here",
            rewrite_style="公众号",
            rewritten_at=datetime(2026, 1, 1, 12, 0, 0),
        )
        assert packet.stage == PipelineStage.REWRITTEN
        assert packet.rewritten_title == "Rewritten Title"

    def test_split_stage(self):
        packet = ContentPacket(
            id="pkt-004",
            source_platform="baidu",
            source_url="https://example.com",
            source_title="Title",
            source_content="Content",
            split_result={"sentences": [], "scenes": []},
            total_scenes=5,
            total_duration=30.0,
        )
        assert packet.total_scenes == 5
        assert packet.total_duration == 30.0

    def test_video_stage(self):
        packet = ContentPacket(
            id="pkt-005",
            source_platform="baidu",
            source_url="https://example.com",
            source_title="Title",
            source_content="Content",
            video_url="https://storage.com/video.mp4",
            video_duration=60.0,
        )
        assert packet.video_url == "https://storage.com/video.mp4"

    def test_with_tags_and_metadata(self):
        packet = ContentPacket(
            id="pkt-006",
            source_platform="baidu",
            source_url="https://example.com",
            source_title="Title",
            source_content="Content",
            tags=["tech", "AI"],
            metadata={"source_ip": "1.2.3.4"},
        )
        assert "AI" in packet.tags
        assert packet.metadata["source_ip"] == "1.2.3.4"

    def test_failed_stage(self):
        packet = ContentPacket(
            id="pkt-007",
            source_platform="baidu",
            source_url="https://example.com",
            source_title="Title",
            source_content="Content",
            stage=PipelineStage.FAILED,
            error="API rate limit exceeded",
        )
        assert packet.error == "API rate limit exceeded"

    def test_extra_allowed(self):
        packet = ContentPacket(
            id="pkt-008",
            source_platform="baidu",
            source_url="https://example.com",
            source_title="Title",
            source_content="Content",
            custom_field="should_not_raise",
        )
        assert packet.model_extra.get("custom_field") == "should_not_raise"

    def test_from_dict(self):
        data = {
            "id": "pkt-009",
            "source_platform": "weibo",
            "source_url": "https://weibo.com/x",
            "source_title": "T",
            "source_content": "C",
            "tags": ["tech"],
            "metadata": {"key": "val"},
        }
        packet = ContentPacket(**data)
        assert packet.tags == ["tech"]
        assert packet.metadata["key"] == "val"


class TestScenePrompt:
    """ScenePrompt model"""

    def test_minimal(self):
        sp = ScenePrompt(scene_id=0, text="A man walks into a bar", prompt="A cinematic shot of a bar entrance")
        assert sp.scene_id == 0
        assert sp.duration == 5.0
        assert sp.subtitle_text == ""

    def test_full(self):
        sp = ScenePrompt(
            scene_id=1,
            title="The Meeting",
            text="Two people discuss at a table",
            prompt="Wide shot of two people in a conference room",
            subtitle_text="Hello, let's begin.",
            duration=8.0,
            character="Alice",
            setting="Conference Room",
            mood="Professional",
        )
        assert sp.title == "The Meeting"
        assert sp.character == "Alice"
        assert sp.mood == "Professional"

    def test_zero_duration_not_allowed(self):
        with pytest.raises(Exception):
            ScenePrompt(scene_id=0, text="text", prompt="prompt", duration=0)


class TestVideoAsset:
    """VideoAsset model"""

    def test_minimal(self):
        scenes = [ScenePrompt(scene_id=0, text="Scene text", prompt="Scene prompt")]
        asset = VideoAsset(id="vid-001", title="My Video", scenes=scenes)
        assert asset.title == "My Video"
        assert len(asset.scenes) == 1
        assert asset.style == "写实"
        assert asset.resolution == "1080x1920"
        assert asset.fps == 30

    def test_custom_values(self):
        scenes = [ScenePrompt(scene_id=0, text="T", prompt="P")]
        asset = VideoAsset(
            id="vid-002",
            title="Custom Video",
            scenes=scenes,
            style="动漫",
            platform="B站",
            voice_type="标准男声",
            subtitle_enabled=False,
            resolution="1920x1080",
            fps=24,
        )
        assert asset.style == "动漫"
        assert asset.platform == "B站"
        assert asset.subtitle_enabled is False
        assert asset.fps == 24

    def test_background_music(self):
        scenes = [ScenePrompt(scene_id=0, text="T", prompt="P")]
        asset = VideoAsset(
            id="vid-003",
            title="Music Video",
            scenes=scenes,
            background_music="/music/bg.mp3",
        )
        assert asset.background_music == "/music/bg.mp3"

    def test_empty_scenes_raises(self):
        with pytest.raises(Exception):
            VideoAsset(id="vid-004", title="Empty", scenes=[])

    def test_fps_out_of_range_raises(self):
        scenes = [ScenePrompt(scene_id=0, text="T", prompt="P")]
        with pytest.raises(Exception):
            VideoAsset(id="vid-005", title="Bad", scenes=scenes, fps=10)

    def test_extra_allowed(self):
        scenes = [ScenePrompt(scene_id=0, text="T", prompt="P")]
        asset = VideoAsset(id="vid-006", title="Extra", scenes=scenes, custom="value")
        assert asset.model_extra.get("custom") == "value"

    def test_with_metadata(self):
        scenes = [ScenePrompt(scene_id=0, text="T", prompt="P")]
        asset = VideoAsset(
            id="vid-007",
            title="Meta",
            scenes=scenes,
            metadata={"renderer": "ffmpeg", "quality": "high"},
        )
        assert asset.metadata["renderer"] == "ffmpeg"
