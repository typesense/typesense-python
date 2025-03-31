"""Fixtures for the Metrics class tests."""

import pytest

from typesense.api_call import ApiCall
from typesense.metrics import Metrics


@pytest.fixture(scope="function", name="actual_metrics")
def actual_debug_fixture(actual_api_call: ApiCall) -> Metrics:
    """Return a Debug object using a real API."""
    return Metrics(actual_api_call)
