"""Fixtures for the synonym set tests."""

import pytest
import requests

from typesense.api_call import ApiCall
from typesense.synonym_set import SynonymSet
from typesense.synonym_sets import SynonymSets


@pytest.fixture(scope="function", name="create_synonym_set")
def create_synonym_set_fixture() -> None:
    """Create a synonym set in the Typesense server."""
    url = "http://localhost:8108/synonym_sets/test-set"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}
    data = {
        "items": [
            {
                "id": "company_synonym",
                "synonyms": ["companies", "corporations", "firms"],
            }
        ]
    }

    resp = requests.put(url, headers=headers, json=data, timeout=3)
    resp.raise_for_status()


@pytest.fixture(scope="function", name="delete_all_synonym_sets")
def clear_typesense_synonym_sets() -> None:
    """Remove all synonym sets from the Typesense server."""
    url = "http://localhost:8108/synonym_sets"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}

    # Get the list of synonym sets
    response = requests.get(url, headers=headers, timeout=3)
    response.raise_for_status()
    data = response.json()

    # Delete each synonym set
    for synset in data:
        name = synset.get("name")
        if not name:
            continue
        delete_url = f"{url}/{name}"
        delete_response = requests.delete(delete_url, headers=headers, timeout=3)
        delete_response.raise_for_status()


@pytest.fixture(scope="function", name="actual_synonym_sets")
def actual_synonym_sets_fixture(actual_api_call: ApiCall) -> SynonymSets:
    """Return a SynonymSets object using a real API."""
    return SynonymSets(actual_api_call)


@pytest.fixture(scope="function", name="actual_synonym_set")
def actual_synonym_set_fixture(actual_api_call: ApiCall) -> SynonymSet:
    """Return a SynonymSet object using a real API."""
    return SynonymSet(actual_api_call, "test-set")


@pytest.fixture(scope="function", name="fake_synonym_sets")
def fake_synonym_sets_fixture(fake_api_call: ApiCall) -> SynonymSets:
    """Return a SynonymSets object with test values."""
    return SynonymSets(fake_api_call)


@pytest.fixture(scope="function", name="fake_synonym_set")
def fake_synonym_set_fixture(fake_api_call: ApiCall) -> SynonymSet:
    """Return a SynonymSet object with test values."""
    return SynonymSet(fake_api_call, "test-set")


