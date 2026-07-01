"""Tests for shared_models.trendscope — aligned with trendscope serialization shapes."""
from shared_models.trendscope.models import (
    HotArticleModel,
    PlatformModel,
    TrendingListResponse,
    TrendingPipelineItem,
    TrendingTopicModel,
)


class TestPlatformModel:
    """PlatformModel — now has id as required field"""

    def test_minimal(self):
        p = PlatformModel(id=1, code="douyin", name="抖音")
        assert p.code == "douyin"
        assert p.is_active is True
        assert p.category == "general"

    def test_full(self):
        p = PlatformModel(
            id=2, code="baidu", name="百度",
            icon_url="https://baidu.com/favicon.ico",
            category="search", is_active=False,
        )
        assert p.icon_url == "https://baidu.com/favicon.ico"
        assert p.category == "search"
        assert p.is_active is False


class TestTrendingTopicModel:
    """TrendingTopicModel — platform is now nested dict, snapshot_at is str"""

    def test_minimal(self):
        t = TrendingTopicModel(platform={"code": "weibo"}, rank=1, title="Hot Topic", hot_value="1000000")
        assert t.rank == 1
        assert t.hot_value == "1000000"
        assert t.topic_url == ""

    def test_with_all(self):
        t = TrendingTopicModel(
            id=42,
            platform={"code": "baidu", "name": "百度"},
            rank=5,
            title="AI News",
            hot_value="500000",
            hot_value_norm=80.5,
            topic_url="https://baidu.com/topic",
            category="tech",
            snapshot_at="2026-06-01T10:00:00",
        )
        assert t.id == 42
        assert t.platform == {"code": "baidu", "name": "百度"}
        assert t.hot_value_norm == 80.5
        assert t.snapshot_at == "2026-06-01T10:00:00"


class TestHotArticleModel:
    """HotArticleModel — platform is now nested dict, snapshot_at/publish_at are str"""

    def test_minimal(self):
        a = HotArticleModel(platform={"code": "douyin"}, title="Funny Cat", source_url="https://douyin.com/v/1")
        assert a.read_count == 0

    def test_with_engagement(self):
        a = HotArticleModel(
            platform={"code": "xiaohongshu", "name": "小红书"},
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
            platform={"code": "douyin"},
            title="Art Tutorial",
            source_url="https://douyin.com/v/2",
            images=[{"url": "https://example.com/img1.jpg"}, {"url": "https://example.com/img2.jpg"}],
        )
        assert len(a.images) == 2

    def test_video_url(self):
        a = HotArticleModel(
            platform={"code": "douyin"},
            title="Video Test",
            source_url="https://douyin.com/v/3",
            video_url="https://douyin.com/play/123",
        )
        assert a.video_url == "https://douyin.com/play/123"


class TestTrendingPipelineItem:
    """TrendingPipelineItem — platform is now nested dict"""

    def test_minimal(self):
        item = TrendingPipelineItem(
            source_url="https://example.com",
            title="Trending Article",
            platform={"code": "weibo"},
        )
        assert item.read_count == 0

    def test_full(self):
        item = TrendingPipelineItem(
            source_url="https://example.com/2",
            title="Viral Post",
            platform={"code": "douyin", "name": "抖音"},
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
            TrendingTopicModel(platform={"code": "weibo"}, rank=1, title="T1", hot_value="100"),
            TrendingTopicModel(platform={"code": "weibo"}, rank=2, title="T2", hot_value="50"),
        ]
        resp = TrendingListResponse(items=items, total=2, page=1, page_size=20)
        assert len(resp.items) == 2
        assert resp.total == 2
