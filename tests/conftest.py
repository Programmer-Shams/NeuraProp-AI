"""Root conftest — shared fixtures for all tests."""

import os
import pytest

# Ensure test environment
os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("ENCRYPTION_KEY", "")
os.environ.setdefault("CLERK_SECRET_KEY", "test-secret-key-for-jwt-signing-32chars")


@pytest.fixture
def firm_id() -> str:
    return "550e8400-e29b-41d4-a716-446655440000"


@pytest.fixture
def trader_id() -> str:
    return "660e8400-e29b-41d4-a716-446655440001"


@pytest.fixture
def api_key() -> str:
    return "np_live_testfirm_abcdef1234567890"
