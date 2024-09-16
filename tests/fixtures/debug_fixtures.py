"""Fixtures for the Debug class tests."""

import pytest

from typesense.api_call import ApiCall
from typesense.debug import Debug


@pytest.fixture(scope="function", name="actual_debug")
def actual_debug_fixture(actual_api_call: ApiCall) -> Debug:
    """Return a Debug object using a real API."""
    return Debug(actual_api_call)


@pytest.fixture(scope="function", name="fake_debug")
def fake_debug_fixture(fake_api_call: ApiCall) -> Debug:
    """Return a debug object with test values."""
    return Debug(fake_api_call)
