"""Fixtures for the MultiSearch class."""

import pytest

from typesense.api_call import ApiCall
from typesense.multi_search import MultiSearch


@pytest.fixture(scope="function", name="actual_multi_search")
def actual_multi_search_fixture(actual_api_call: ApiCall) -> MultiSearch:
    """Return a MultiSearch object using a real API."""
    return MultiSearch(actual_api_call)
