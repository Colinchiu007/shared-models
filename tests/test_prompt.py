"""Tests for shared_models.prompt — OptimizeRequest, OptimizeResult, ReverseRequest, ReverseResult"""
import pytest
from shared_models.prompt import OptimizeRequest, OptimizeResult, ReverseRequest, ReverseResult


class TestOptimizeRequest:
    """OptimizeRequest validation"""

    def test_minimal(self):
        req = OptimizeRequest(raw_prompt="a cat sitting on a chair")
        assert req.raw_prompt == "a cat sitting on a chair"
        assert req.target_platform == "通用"
        assert req.language == "zh"
        assert req.num_candidates == 1

    def test_empty_raises(self):
        with pytest.raises(Exception):
            OptimizeRequest(raw_prompt="")

    def test_custom_platform(self):
        req = OptimizeRequest(raw_prompt="dog", target_platform="Midjourney", language="en", num_candidates=3)
        assert req.target_platform == "Midjourney"
        assert req.language == "en"
        assert req.num_candidates == 3

    def test_with_style(self):
        req = OptimizeRequest(raw_prompt="cat", style="anime")
        assert req.style == "anime"


class TestOptimizeResult:
    """OptimizeResult model"""

    def test_minimal(self):
        result = OptimizeResult(
            raw_prompt="cat",
            optimized_prompt="A detailed digital illustration of a cat",
            platform="Midjourney",
        )
        assert result.raw_prompt == "cat"
        assert result.optimized_prompt == "A detailed digital illustration of a cat"
        assert result.tokens_used == 0

    def test_with_tokens(self):
        result = OptimizeResult(
            raw_prompt="dog",
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
        assert req.target_platform == "通用"

    def test_custom_platform(self):
        req = ReverseRequest(image_url="https://example.com/img.jpg", target_platform="Stable Diffusion")
        assert req.target_platform == "Stable Diffusion"


class TestReverseResult:
    """ReverseResult model"""

    def test_minimal(self):
        result = ReverseResult(
            image_url="https://example.com/image.png",
            guessed_prompt="A sunset over mountains",
            platform="Midjourney",
        )
        assert result.confidence == 0.0

    def test_with_confidence(self):
        result = ReverseResult(
            image_url="https://example.com/img.png",
            guessed_prompt="A cat",
            platform="DALL·E",
            confidence=0.85,
        )
        assert result.confidence == 0.85
