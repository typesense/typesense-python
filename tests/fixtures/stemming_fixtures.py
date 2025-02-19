"""Fixtures for the Analytics Rules tests."""

import pytest

from typesense.api_call import ApiCall
from typesense.stemming import Stemming


@pytest.fixture(scope="function", name="actual_stemming")
def actual_stemming_fixture(
    actual_api_call: ApiCall,
) -> Stemming:
    """Return a Stemming object using a real API."""
    return Stemming(actual_api_call)
