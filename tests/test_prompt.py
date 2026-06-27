"""Tests for shared_models.prompt — OptimizeRequest, OptimizeResult, ReverseRequest, ReverseResult"""
import pytest
from shared_models.prompt import OptimizeRequest, OptimizeResult, ReverseRequest, ReverseResult


class TestOptimizeRequest:
    """OptimizeRequest validation"""

    def test_minimal(self):
        req = OptimizeRequest(prompt="a cat sitting on a chair")
        assert req.prompt == "a cat sitting on a chair"
        assert req.platform == "通用"
        assert req.style is None
        assert req.num_candidates == 1
        assert req.creative_level == 5

    def test_empty_raises(self):
        with pytest.raises(Exception):
            OptimizeRequest(prompt="")

    def test_custom_platform(self):
        req = OptimizeRequest(prompt="dog", platform="Midjourney", num_candidates=3, creative_level=8)
        assert req.platform == "Midjourney"
        assert req.num_candidates == 3
        assert req.creative_level == 8

    def test_with_style(self):
        req = OptimizeRequest(prompt="cat", style="anime")
        assert req.style == "anime"


class TestOptimizeResult:
    """OptimizeResult model"""

    def test_minimal(self):
        result = OptimizeResult(
            optimized_prompt="A detailed digital illustration of a cat",
            platform="Midjourney",
        )
        assert result.optimized_prompt == "A detailed digital illustration of a cat"
        assert result.tokens_used == 0

    def test_with_tokens(self):
        result = OptimizeResult(
            optimized_prompt="A cute dog",
            platform="DALL·E",
            tokens_used=150,
        )
        assert result.tokens_used == 150


class TestReverseRequest:
    """ReverseRequest model"""

    def test_minimal(self):
        req = ReverseRequest(image_url="https://example.com/image.png")
        assert req.image_url == "https://example.com/image.png"
        assert req.platform == "通用"

    def test_custom_platform(self):
        req = ReverseRequest(image_url="https://example.com/img.jpg", platform="Stable Diffusion")
        assert req.platform == "Stable Diffusion"


class TestReverseResult:
    """ReverseResult model"""

    def test_minimal(self):
        result = ReverseResult(
            image_url="https://example.com/image.png",
            prompt="A sunset over mountains",
            platform="Midjourney",
        )
        assert result.confidence == 0.0

    def test_with_confidence(self):
        result = ReverseResult(
            image_url="https://example.com/img.png",
            prompt="A cat",
            platform="DALL·E",
            confidence=0.85,
        )
        assert result.confidence == 0.85
