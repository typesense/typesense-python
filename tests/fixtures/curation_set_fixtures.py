"""Fixtures for the curation set tests."""

import pytest
import requests

from typesense.api_call import ApiCall
from typesense.curation_set import CurationSet
from typesense.curation_sets import CurationSets


@pytest.fixture(scope="function", name="create_curation_set")
def create_curation_set_fixture() -> None:
    """Create a curation set in the Typesense server."""
    url = "http://localhost:8108/curation_sets/products"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}
    data = {
        "items": [
            {
                "id": "rule-1",
                "rule": {"query": "shoe", "match": "contains"},
                "includes": [{"id": "123", "position": 1}],
                "excludes": [{"id": "999"}],
            }
        ]
    }

    resp = requests.put(url, headers=headers, json=data, timeout=3)
    resp.raise_for_status()


@pytest.fixture(scope="function", name="delete_all_curation_sets")
def clear_typesense_curation_sets() -> None:
    """Remove all curation sets from the Typesense server."""
    url = "http://localhost:8108/curation_sets"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}

    response = requests.get(url, headers=headers, timeout=3)
    response.raise_for_status()
    data = response.json()

    for cur in data:
        name = cur.get("name")
        if not name:
            continue
        delete_url = f"{url}/{name}"
        delete_response = requests.delete(delete_url, headers=headers, timeout=3)
        delete_response.raise_for_status()


@pytest.fixture(scope="function", name="actual_curation_sets")
def actual_curation_sets_fixture(actual_api_call: ApiCall) -> CurationSets:
    """Return a CurationSets object using a real API."""
    return CurationSets(actual_api_call)


@pytest.fixture(scope="function", name="actual_curation_set")
def actual_curation_set_fixture(actual_api_call: ApiCall) -> CurationSet:
    """Return a CurationSet object using a real API."""
    return CurationSet(actual_api_call, "products")


@pytest.fixture(scope="function", name="fake_curation_sets")
def fake_curation_sets_fixture(fake_api_call: ApiCall) -> CurationSets:
    """Return a CurationSets object with test values."""
    return CurationSets(fake_api_call)


@pytest.fixture(scope="function", name="fake_curation_set")
def fake_curation_set_fixture(fake_api_call: ApiCall) -> CurationSet:
    """Return a CurationSet object with test values."""
    return CurationSet(fake_api_call, "products")


