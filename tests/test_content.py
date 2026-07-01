"""Tests for shared_models.content — CollectRequest, CollectResult, RewriteRequest, RewriteResult"""
import pytest
from datetime import datetime
from shared_models.content import CollectRequest, CollectResult, RewriteRequest, RewriteResult


class TestCollectRequest:
    """CollectRequest — URL content collection request"""

    def test_minimal(self):
        req = CollectRequest(url="https://example.com/article")
        assert req.url == "https://example.com/article"
        assert req.source == "manual"
        assert req.platform is None

    def test_with_all_fields(self):
        req = CollectRequest(
            url="https://douyin.com/video/123",
            source="trendscope",
            platform="douyin",
        )
        assert req.source == "trendscope"
        assert req.platform == "douyin"

    def test_empty_url_allowed(self):
        req = CollectRequest(url="")
        assert req.url == ""


class TestCollectResult:
    """CollectResult — URL content collection result"""

    def test_minimal(self):
        result = CollectResult(source_url="https://example.com")
        assert result.source_url == "https://example.com"
        assert result.title == ""
        assert result.author is None

    def test_with_data(self):
        result = CollectResult(
            title="Test Article",
            content="Full article content here...",
            source_url="https://example.com/article",
            author="John Doe",
            word_count=500,
        )
        assert result.title == "Test Article"
        assert result.author == "John Doe"
        assert result.word_count == 500


class TestRewriteRequest:
    """RewriteRequest — AI rewrite request"""

    def test_minimal(self):
        req = RewriteRequest(content="Original text to rewrite")
        assert req.content == "Original text to rewrite"
        assert req.style == "default"
        assert req.length == "medium"
        assert req.seo_optimize is False

    def test_with_all_fields(self):
        req = RewriteRequest(
            content="Source content",
            title="Original Title",
            style="eye-catching",
            length="short",
            target_platform="xiaohongshu",
            seo_optimize=True,
        )
        assert req.style == "eye-catching"
        assert req.target_platform == "xiaohongshu"
        assert req.seo_optimize is True


class TestRewriteResult:
    """RewriteResult — AI rewrite result"""

    def test_minimal(self):
        result = RewriteResult(rewritten_content="Rewritten content here")
        assert result.rewritten_content == "Rewritten content here"
        assert result.rewritten_title == ""
        assert result.word_count == 0

    def test_with_data(self):
        result = RewriteResult(
            rewritten_title="New Title",
            rewritten_content="Full rewritten content...",
            style="eye-catching",
            word_count=450,
            model_used="gpt-4o",
        )
        assert result.rewritten_title == "New Title"
        assert result.word_count == 450
        assert result.model_used == "gpt-4o"

    def test_datetime_default(self):
        result = RewriteResult(rewritten_content="Content")
        assert isinstance(result.created_at, datetime)
