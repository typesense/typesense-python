"""Fixtures for the Operations tests."""

import pytest

from typesense.api_call import ApiCall
from typesense.operations import Operations


@pytest.fixture(scope="function", name="actual_operations")
def actual_operations_fixture(actual_api_call: ApiCall) -> Operations:
    """Return a Operations object using a real API."""
    return Operations(actual_api_call)


@pytest.fixture(scope="function", name="fake_operations")
def fake_operations_fixture(fake_api_call: ApiCall) -> Operations:
    """Return a Collection object with test values."""
    return Operations(fake_api_call)
