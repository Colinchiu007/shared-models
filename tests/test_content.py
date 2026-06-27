"""Tests for shared_models.content — ContentFetchRequest, RewriteConfig, RewriteResult"""
import pytest
from datetime import datetime
from shared_models.content import ContentFetchRequest, RewriteConfig, RewriteResult


class TestContentFetchRequest:
    """ContentFetchRequest validation"""

    def test_minimal(self):
        req = ContentFetchRequest(url="https://example.com/article")
        assert req.url == "https://example.com/article"
        assert req.source == "manual"
        assert req.style == "default"

    def test_with_all_fields(self):
        req = ContentFetchRequest(
            url="https://douyin.com/video/123",
            source="trendscope",
            platform="douyin",
            style="creative",
        )
        assert req.source == "trendscope"
        assert req.platform == "douyin"
        assert req.style == "creative"

    def test_empty_url_allowed(self):
        """url field doesn't enforce min_length — string type accepts empty"""
        req = ContentFetchRequest(url="")
        assert req.url == ""


class TestRewriteConfig:
    """RewriteConfig model"""

    def test_defaults(self):
        config = RewriteConfig()
        assert config.style == "公众号"
        assert config.length == "medium"
        assert config.target_platform is None

    def test_custom(self):
        config = RewriteConfig(style="小红书", length="short", target_platform="xiaohongshu")
        assert config.style == "小红书"
        assert config.length == "short"
        assert config.target_platform == "xiaohongshu"


class TestRewriteResult:
    """RewriteResult model"""

    def test_minimal(self):
        now = datetime.now()
        result = RewriteResult(
            original_url="https://example.com",
            rewritten_title="Rewritten Title",
            rewritten_content="Content here",
            style="公众号",
            word_count=120,
            model_used="gpt-4o",
            created_at=now,
        )
        assert result.original_url == "https://example.com"
        assert result.word_count == 120
        assert result.model_used == "gpt-4o"
        assert result.created_at == now

    def test_from_iso_format(self):
        dt = datetime.fromisoformat("2026-01-01T12:00:00")
        result = RewriteResult(
            original_url="https://example.com",
            rewritten_title="T",
            rewritten_content="C",
            style="知乎",
            word_count=50,
            model_used="claude-3",
            created_at=dt,
        )
        assert result.style == "知乎"
