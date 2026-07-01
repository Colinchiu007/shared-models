"""Tests for shared_models.llm — LLMProviderConfig, ModelRoute, UserLLMOverride, LLMInvocationRequest, LLMInvocationResponse, LLMGlobalConfig"""
from datetime import datetime
import pytest
from shared_models.llm import (
    LLMGlobalConfig,
    LLMInvocationRequest,
    LLMInvocationResponse,
    LLMProviderConfig,
    ModelRoute,
    UserLLMOverride,
)


class TestLLMProviderConfig:
    """LLMProviderConfig validation"""

    def test_minimal(self):
        cfg = LLMProviderConfig(name="openai", provider_type="openai_compat")
        assert cfg.name == "openai"
        assert cfg.temperature == 0.7
        assert cfg.max_tokens == 4096
        assert cfg.enabled is True
        assert cfg.min_tier == 1

    def test_custom_values(self):
        cfg = LLMProviderConfig(
            name="doubao",
            provider_type="doubao",
            base_url="https://api.doubao.com/v1",
            api_key="sk-test",
            display_name="豆包",
            models=["doubao-pro", "doubao-lite"],
            default_model="doubao-pro",
            temperature=0.3,
            max_tokens=8192,
            timeout=120,
            priority=10,
            min_tier=2,
            enabled=False,
        )
        assert cfg.default_model == "doubao-pro"
        assert cfg.temperature == 0.3
        assert cfg.max_tokens == 8192
        assert cfg.priority == 10

    def test_extra_config(self):
        cfg = LLMProviderConfig(
            name="openai",
            provider_type="openai_compat",
            extra_config={"organization_id": "org-123"},
        )
        assert cfg.extra_config["organization_id"] == "org-123"

    def test_with_timestamps(self):
        now = datetime.now()
        cfg = LLMProviderConfig(
            name="test",
            provider_type="openai_compat",
            id="uuid-123",
            created_at=now,
            updated_at=now,
        )
        assert cfg.id == "uuid-123"
        assert cfg.created_at == now


class TestModelRoute:
    """ModelRoute validation"""

    def test_minimal(self):
        route = ModelRoute(category="quick", provider="openai", model="gpt-4o-mini")
        assert route.category == "quick"
        assert route.provider == "openai"
        assert route.cost_level == "medium"

    def test_custom(self):
        route = ModelRoute(
            category="deep",
            provider="openai",
            model="gpt-4o",
            fallback_model="gpt-4o-mini",
            keywords=["code", "debug", "architecture"],
            description="Complex coding tasks",
            cost_level="high",
            priority=5,
        )
        assert route.fallback_model == "gpt-4o-mini"
        assert len(route.keywords) == 3
        assert route.cost_level == "high"

    def test_defaults(self):
        route = ModelRoute(category="creative", provider="minimax", model="minimax-pro")
        assert route.keywords == []
        assert route.usage_count == 0
        assert route.description == ""


class TestUserLLMOverride:
    """UserLLMOverride model"""

    def test_minimal(self):
        override = UserLLMOverride(user_uuid="user-1", provider_name="openai", api_key="sk-user-key")
        assert override.user_uuid == "user-1"
        assert override.is_active is True

    def test_custom(self):
        override = UserLLMOverride(
            user_uuid="user-2",
            provider_name="doubao",
            api_key="sk-user-2",
            base_url="https://custom.endpoint.com",
            model="doubao-pro",
            is_active=False,
        )
        assert override.base_url == "https://custom.endpoint.com"
        assert override.model == "doubao-pro"
        assert override.is_active is False


class TestLLMInvocationRequest:
    """LLMInvocationRequest model"""

    def test_minimal(self):
        req = LLMInvocationRequest(messages=[{"role": "user", "content": "Hello"}])
        assert len(req.messages) == 1
        assert req.stream is False

    def test_with_system_prompt(self):
        req = LLMInvocationRequest(
            messages=[{"role": "user", "content": "Hi"}],
            system_prompt="You are helpful",
        )
        assert req.system_prompt == "You are helpful"

    def test_direct_resolution(self):
        req = LLMInvocationRequest(
            messages=[{"role": "user", "content": "Hi"}],
            provider="openai",
            model="gpt-4o",
            temperature=0.5,
            max_tokens=2048,
        )
        assert req.provider == "openai"
        assert req.model == "gpt-4o"
        assert req.temperature == 0.5
        assert req.category is None

    def test_route_resolution(self):
        req = LLMInvocationRequest(
            messages=[{"role": "user", "content": "Write a poem"}],
            category="creative",
            user_uuid="user-1",
        )
        assert req.category == "creative"
        assert req.user_uuid == "user-1"
        assert req.provider is None

    def test_streaming(self):
        req = LLMInvocationRequest(
            messages=[{"role": "user", "content": "Hello"}],
            stream=True,
            stream_callback_url="https://callback.com/stream",
        )
        assert req.stream is True
        assert req.stream_callback_url == "https://callback.com/stream"


class TestLLMInvocationResponse:
    """LLMInvocationResponse model"""

    def test_minimal(self):
        resp = LLMInvocationResponse(content="Hello, world!")
        assert resp.content == "Hello, world!"
        assert resp.model == ""
        assert resp.finish_reason == "stop"
        assert resp.input_tokens == 0

    def test_full(self):
        resp = LLMInvocationResponse(
            content="Generated text",
            model="gpt-4o",
            provider="openai",
            finish_reason="length",
            input_tokens=50,
            output_tokens=200,
            total_tokens=250,
            latency_ms=1200,
        )
        assert resp.model == "gpt-4o"
        assert resp.finish_reason == "length"
        assert resp.total_tokens == 250
        assert resp.latency_ms == 1200

    def test_created_at_set(self):
        resp = LLMInvocationResponse(content="Test")
        assert resp.created_at is not None

    def test_created_at_timezone(self):
        resp = LLMInvocationResponse(content="Test")
        assert resp.created_at.tzinfo is not None


class TestLLMGlobalConfig:
    """LLMGlobalConfig — aggregated config with lookup helpers"""

    def test_empty(self):
        cfg = LLMGlobalConfig()
        assert cfg.providers == []
        assert cfg.routing == []
        assert cfg.default_temperature == 0.7

    def test_get_provider_found(self):
        providers = [
            LLMProviderConfig(name="openai", provider_type="openai_compat"),
            LLMProviderConfig(name="doubao", provider_type="doubao"),
        ]
        cfg = LLMGlobalConfig(providers=providers)
        found = cfg.get_provider("openai")
        assert found is not None
        assert found.name == "openai"
        assert cfg.get_provider("nonexistent") is None

    def test_get_route_found(self):
        routes = [
            ModelRoute(category="quick", provider="openai", model="gpt-4o-mini"),
            ModelRoute(category="deep", provider="openai", model="gpt-4o"),
        ]
        cfg = LLMGlobalConfig(routing=routes)
        found = cfg.get_route("deep")
        assert found is not None
        assert found.model == "gpt-4o"
        assert cfg.get_route("unknown") is None

    def test_get_user_override_found(self):
        overrides = [
            UserLLMOverride(user_uuid="u1", provider_name="openai", api_key="sk-u1"),
            UserLLMOverride(user_uuid="u2", provider_name="openai", api_key="sk-u2", is_active=False),
        ]
        cfg = LLMGlobalConfig(user_overrides=overrides)
        found = cfg.get_user_override("u1", "openai")
        assert found is not None
        assert found.api_key == "sk-u1"
        # Inactive override should not be returned
        assert cfg.get_user_override("u2", "openai") is None
        assert cfg.get_user_override("u1", "doubao") is None
