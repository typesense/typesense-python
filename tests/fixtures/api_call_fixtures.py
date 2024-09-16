"""Fixtures for ApiCall tests."""

import pytest

from typesense.api_call import ApiCall
from typesense.configuration import Configuration


@pytest.fixture(scope="function", name="fake_api_call")
def fake_api_call_fixture(
    fake_config: Configuration,
) -> ApiCall:
    """Return an ApiCall object with test values."""
    return ApiCall(fake_config)


@pytest.fixture(scope="function", name="actual_api_call")
def actual_api_call_fixture(actual_config: Configuration) -> ApiCall:
    """Return an ApiCall object using a real API."""
    return ApiCall(actual_config)
