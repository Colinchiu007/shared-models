"""Shared-models test configuration"""
import pytest
from datetime import datetime, timezone


@pytest.fixture
def sample_jwt_secret() -> str:
    return "test-secret-key-for-shared-models-tests"


@pytest.fixture
def utc_now() -> datetime:
    return datetime.now(timezone.utc)
