"""Tests for shared_models.trendscope — PlatformModel, TrendingTopicModel, HotArticleModel, TrendingPipelineItem, TrendingListResponse"""
from datetime import datetime
from shared_models.trendscope.models import (
    HotArticleModel,
    PlatformModel,
    TrendingListResponse,
    TrendingPipelineItem,
    TrendingTopicModel,
)


class TestPlatformModel:
    """PlatformModel"""

    def test_minimal(self):
        p = PlatformModel(code="douyin", name="抖音")
        assert p.code == "douyin"
        assert p.is_active is True
        assert p.category == "general"


class TestTrendingTopicModel:
    """TrendingTopicModel"""

    def test_minimal(self):
        t = TrendingTopicModel(platform_code="weibo", rank=1, title="Hot Topic", hot_value="1000000")
        assert t.rank == 1
        assert t.hot_value == "1000000"
        assert t.topic_url is None

    def test_with_all(self):
        t = TrendingTopicModel(
            id=42,
            platform_code="baidu",
            rank=5,
            title="AI News",
            hot_value="500000",
            hot_value_norm=80.5,
            topic_url="https://baidu.com/topic",
            category="tech",
            snapshot_at=datetime(2026, 6, 1, 10, 0, 0),
        )
        assert t.id == 42
        assert t.hot_value_norm == 80.5


class TestHotArticleModel:
    """HotArticleModel"""

    def test_minimal(self):
        a = HotArticleModel(platform_code="douyin", title="Funny Cat", source_url="https://douyin.com/v/1")
        assert a.read_count == 0

    def test_with_engagement(self):
        a = HotArticleModel(
            platform_code="xiaohongshu",
            title="Skin Care Tips",
            summary="10 tips for better skin",
            source_url="https://xhslink.com/abc",
            like_count=5000,
            comment_count=300,
            share_count=1200,
            favor_count=800,
            collected_count=200,
            author_followers=100000,
            viral_score=85.0,
            viral_score_norm=92.0,
        )
        assert a.favor_count == 800
        assert a.collected_count == 200
        assert a.viral_score == 85.0
        assert a.author_followers == 100000

    def test_with_images(self):
        a = HotArticleModel(
            platform_code="douyin",
            title="Art Tutorial",
            source_url="https://douyin.com/v/2",
            images=[{"url": "https://example.com/img1.jpg"}, {"url": "https://example.com/img2.jpg"}],
        )
        assert len(a.images) == 2


class TestTrendingPipelineItem:
    """TrendingPipelineItem"""

    def test_minimal(self):
        item = TrendingPipelineItem(
            source_url="https://example.com",
            title="Trending Article",
            platform_code="weibo",
        )
        assert item.read_count == 0

    def test_full(self):
        item = TrendingPipelineItem(
            source_url="https://example.com/2",
            title="Viral Post",
            platform_code="douyin",
            summary="This is trending",
            author_name="Creator",
            read_count=50000,
            like_count=15000,
        )
        assert item.author_name == "Creator"
        assert item.like_count == 15000


class TestTrendingListResponse:
    """TrendingListResponse"""

    def test_empty(self):
        resp = TrendingListResponse(items=[], total=0)
        assert resp.total == 0
        assert resp.page == 1
        assert resp.page_size == 20

    def test_with_items(self):
        items = [
            TrendingTopicModel(platform_code="weibo", rank=1, title="T1", hot_value="100"),
            TrendingTopicModel(platform_code="weibo", rank=2, title="T2", hot_value="50"),
        ]
        resp = TrendingListResponse(items=items, total=2, page=1, page_size=20)
        assert len(resp.items) == 2
        assert resp.total == 2
