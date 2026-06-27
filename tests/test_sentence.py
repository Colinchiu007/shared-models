"""Tests for shared_models.sentence — SentenceBlock, SubtitleBlock, SceneSegment, SplitResult"""
import pytest
from shared_models.sentence import SentenceBlock, SubtitleBlock, SceneSegment, SplitResult


class TestSentenceBlock:
    """SentenceBlock model"""

    def test_minimal(self):
        s = SentenceBlock(text="Hello world", index=0)
        assert s.text == "Hello world"
        assert s.index == 0
        assert s.language == "zh"
        assert s.tier == "tier3_rule"
        assert s.confidence == 1.0
        assert s.is_topic_boundary is False

    def test_full(self):
        s = SentenceBlock(
            text="This is a test sentence.",
            index=1,
            char_count=26,
            word_count=5,
            words=["This", "is", "a", "test", "sentence"],
            pos_tags=["DT", "VBZ", "DT", "NN", "."],
            language="en",
            tier="tier2_ml",
            confidence=0.95,
            is_topic_boundary=True,
            topic_depth_score=0.8,
            length_status="ok",
            length_strategy_applied="none",
        )
        assert s.word_count == 5
        assert s.tier == "tier2_ml"
        assert s.topic_depth_score == 0.8

    def test_default_lists(self):
        s = SentenceBlock(text="Test", index=0)
        assert s.words == []
        assert s.pos_tags == []


class TestSubtitleBlock:
    """SubtitleBlock model"""

    def test_minimal(self):
        sub = SubtitleBlock(text="Hello", display_order=0, start_time=0.0, duration=2.5, parent_segment_id=0)
        assert sub.text == "Hello"
        assert sub.duration == 2.5

    def test_positive_duration(self):
        sub = SubtitleBlock(text="Hello", display_order=0, start_time=1.0, duration=3.0, parent_segment_id=1)
        assert sub.start_time == 1.0
        assert sub.parent_segment_id == 1


class TestSceneSegment:
    """SceneSegment model"""

    def test_minimal(self):
        segment = SceneSegment(text="Scene text", segment_id=0, estimated_duration=10.0, target_words=50)
        assert segment.text == "Scene text"
        assert segment.segment_id == 0
        assert segment.sentences == []
        assert segment.subtitles == []

    def test_with_sentences(self):
        sentences = [
            SentenceBlock(text="First sentence", index=0),
            SentenceBlock(text="Second sentence", index=1),
        ]
        segment = SceneSegment(
            text="Full scene",
            segment_id=1,
            estimated_duration=15.0,
            target_words=100,
            sentences=sentences,
        )
        assert len(segment.sentences) == 2
        assert segment.sentences[1].text == "Second sentence"

    def test_with_subtitles(self):
        subs = [SubtitleBlock(text="Sub", display_order=0, start_time=0.0, duration=2.0, parent_segment_id=0)]
        segment = SceneSegment(
            text="Scene", segment_id=0, estimated_duration=2.0, target_words=10,
            subtitles=subs,
        )
        assert len(segment.subtitles) == 1

    def test_optional_fields(self):
        segment = SceneSegment(
            text="Scene", segment_id=0, estimated_duration=5.0, target_words=25,
            era_info={"era": "modern"},
            characters=["Alice", "Bob"],
            setting="Office",
            mood="Serious",
            story_phase="climax",
        )
        assert segment.era_info == {"era": "modern"}
        assert len(segment.characters) == 2
        assert segment.setting == "Office"


class TestSplitResult:
    """SplitResult model"""

    def test_empty(self):
        result = SplitResult()
        assert result.sentences == []
        assert result.scenes == []
        assert result.language == "zh"
        assert result.total_words == 0

    def test_with_data(self):
        sentences = [SentenceBlock(text="Hello", index=0)]
        scenes = [SceneSegment(text="Scene", segment_id=0, estimated_duration=5.0, target_words=10)]
        result = SplitResult(
            sentences=sentences,
            scenes=scenes,
            tier_used="tier1_deepseek",
            language="en",
            total_duration=5.0,
            total_words=1,
            total_scenes=1,
            config_snapshot={"max_sentences": 50},
        )
        assert result.tier_used == "tier1_deepseek"
        assert result.total_scenes == 1
        assert result.total_duration == 5.0
        assert len(result.sentences) == 1

    def test_script_analysis(self):
        result = SplitResult(script_analysis={"key": "value"})
        assert result.script_analysis == {"key": "value"}
