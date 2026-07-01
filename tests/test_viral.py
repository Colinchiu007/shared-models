"""Tests for shared_models.viral — all viral analysis models"""
import pytest
from datetime import datetime
from shared_models.viral import (
    ArticleViralProfile,
    ContentStructure,
    EmotionalTrigger,
    EngagementMetrics,
    TitleAnalysis,
    TitleStructure,
    TrendingInsights,
    ViralAnalysisResult,
    ViralFactor,
    ViralScoringConfig,
)


class TestEnums:
    """Enum models"""

    def test_title_structure_values(self):
        assert TitleStructure.QUESTION.value == "question"
        assert TitleStructure.CURIOSITY_GAP.value == "curiosity_gap"

    def test_emotional_trigger_values(self):
        assert EmotionalTrigger.CURIOSITY.value == "curiosity"
        assert EmotionalTrigger.NONE.value == "none"

    def test_content_structure_values(self):
        assert ContentStructure.LIST.value == "list"
        assert ContentStructure.OTHER.value == "other"


class TestViralFactor:
    """ViralFactor model"""

    def test_minimal(self):
        vf = ViralFactor(name="title_structure")
        assert vf.score == 0.0
        assert vf.confidence == 0.0
        assert vf.evidence == []

    def test_full(self):
        vf = ViralFactor(
            name="emotion",
            label="情感触发",
            score=0.85,
            confidence=0.9,
            evidence=["Uses curiosity gap", "Strong opening hook"],
            details={"emotion_type": "curiosity"},
        )
        assert vf.label == "情感触发"
        assert vf.score == 0.85
        assert vf.details["emotion_type"] == "curiosity"


class TestTitleAnalysis:
    """TitleAnalysis model"""

    def test_minimal(self):
        ta = TitleAnalysis(title="10 Ways to Code Better")
        assert ta.title == "10 Ways to Code Better"
        assert ta.structure == TitleStructure.OTHER
        assert ta.has_numbers is False

    def test_detected_features(self):
        ta = TitleAnalysis(
            title="5 Secrets That Will Shock You! #viral",
            structure=TitleStructure.NUMBERED_LIST,
            length=40,
            word_count=7,
            has_numbers=True,
            has_questions=False,
            has_emojis=True,
            has_colon=False,
            has_power_words=["Secrets", "Shock"],
            emotion=EmotionalTrigger.SURPRISE,
            confidence=0.95,
        )
        assert ta.structure == TitleStructure.NUMBERED_LIST
        assert ta.has_numbers is True
        assert ta.has_emojis is True
        assert EmotionalTrigger.SURPRISE in ta.emotion


class TestEngagementMetrics:
    """EngagementMetrics model"""

    def test_defaults(self):
        em = EngagementMetrics()
        assert em.likes == 0
        assert em.engagement_rate == 0.0
        assert em.viral_score == 0.0

    def test_with_values(self):
        em = EngagementMetrics(
            likes=15000,
            comments=3200,
            shares=5800,
            favorites=900,
            views=500000,
            engagement_rate=0.05,
            viral_score=78.5,
        )
        assert em.likes == 15000
        assert em.engagement_rate == 0.05
        assert em.viral_score == 78.5


class TestArticleViralProfile:
    """ArticleViralProfile model"""

    def test_minimal(self):
        profile = ArticleViralProfile(title_analysis=TitleAnalysis(title="Test"))
        assert profile.overall_score == 0.0
        assert profile.factors == []

    def test_full(self):
        profile = ArticleViralProfile(
            platform_code="xiaohongshu",
            title="Amazing Recipe",
            author_name="Chef",
            author_followers=50000,
            source_url="https://example.com/recipe",
            category="food",
            title_analysis=TitleAnalysis(title="Amazing Recipe"),
            engagement=EngagementMetrics(likes=1000),
            factors=[ViralFactor(name="title", score=0.8)],
            overall_score=75.0,
            rank=3,
        )
        assert profile.platform_code == "xiaohongshu"
        assert profile.overall_score == 75.0
        assert profile.rank == 3
        assert profile.engagement.likes == 1000


class TestViralAnalysisResult:
    """ViralAnalysisResult model"""

    def test_minimal(self):
        result = ViralAnalysisResult(topic="AI Technology")
        assert result.topic == "AI Technology"
        assert result.overall_score == 0.0
        assert result.factors == []

    def test_with_data(self):
        result = ViralAnalysisResult(
            topic="Crypto",
            overall_score=65.0,
            trend_direction="rising",
            confidence=0.8,
            factors=[ViralFactor(name="timeliness", score=0.9)],
            articles=[ArticleViralProfile(
                title="Crypto Boom",
                title_analysis=TitleAnalysis(title="Crypto Boom"),
            )],
            platform_scores={"twitter": 70.0, "reddit": 55.0},
            suggested_angles=["Explain simply", "Risk warning"],
        )
        assert result.trend_direction == "rising"
        assert len(result.articles) == 1
        assert result.platform_scores["twitter"] == 70.0
        assert len(result.suggested_angles) == 2

    def test_analyzed_at_set(self):
        result = ViralAnalysisResult(topic="Test")
        assert result.analyzed_at is not None


class TestTrendingInsights:
    """TrendingInsights model"""

    def test_minimal(self):
        ti = TrendingInsights()
        assert ti.total_items == 0

    def test_with_data(self):
        ti = TrendingInsights(
            platform_code="douyin",
            total_items=100,
            category_distribution={"entertainment": 60, "tech": 40},
            title_structure_distribution={"question": 30, "numbered_list": 20},
            emotion_distribution={"curiosity": 50, "joy": 30},
            top_topics=[{"topic": "AI", "score": 95}],
            rising_keywords=[{"word": "AGI", "delta": 500}],
        )
        assert ti.category_distribution["tech"] == 40
        assert ti.top_topics[0]["score"] == 95


class TestViralScoringConfig:
    """ViralScoringConfig — scoring weights"""

    def test_defaults(self):
        cfg = ViralScoringConfig()
        assert cfg.weight_likes == 0.35
        assert cfg.weight_comments == 0.30
        assert cfg.weight_shares == 0.25
        assert cfg.weight_favorites == 0.10
        assert cfg.w_linear == 0.6
        assert cfg.w_log == 0.3
        assert cfg.w_authority == 0.1

    def test_validate_weights_pass(self):
        cfg = ViralScoringConfig()
        assert cfg.validate_weights() is True

    def test_validate_weights_fail(self):
        cfg = ViralScoringConfig(weight_likes=0.5, weight_comments=0.5, weight_shares=0.5, weight_favorites=0.5)
        assert cfg.validate_weights() is False

    def test_platform_ceilings(self):
        cfg = ViralScoringConfig()
        assert "douyin" in cfg.platform_ceilings
        assert len(cfg.platform_ceilings["douyin"]) == 3
