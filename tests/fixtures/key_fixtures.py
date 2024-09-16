"""Fixtures for the key tests."""

import pytest
import requests

from typesense.api_call import ApiCall
from typesense.key import Key
from typesense.keys import Keys


@pytest.fixture(scope="function", name="delete_all_keys")
def clear_typesense_keys() -> None:
    """Remove all keys from the Typesense server."""
    url = "http://localhost:8108/keys"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}

    # Get the list of keys
    response = requests.get(url, headers=headers, timeout=3)
    response.raise_for_status()

    keys = response.json()

    # Delete each key
    for key in keys["keys"]:
        key_name = key.get("id")
        delete_url = f"{url}/{key_name}"
        delete_response = requests.delete(delete_url, headers=headers, timeout=3)
        delete_response.raise_for_status()


@pytest.fixture(scope="function", name="create_key_id")
def create_key_fixture() -> int:
    """Create a key set in the Typesense server."""
    url = "http://localhost:8108/keys"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}
    api_key_data = {
        "actions": ["documents:search"],
        "collections": ["companies"],
        "description": "Search-only key",
    }

    response = requests.post(url, headers=headers, json=api_key_data, timeout=3)
    response.raise_for_status()
    key_id: int = response.json()["id"]
    return key_id


@pytest.fixture(scope="function", name="actual_keys")
def actual_keys_fixture(actual_api_call: ApiCall) -> Keys:
    """Return a Keys object using a real API."""
    return Keys(actual_api_call)


@pytest.fixture(scope="function", name="fake_keys")
def fake_keys_fixture(fake_api_call: ApiCall) -> Keys:
    """Return a AnalyticsRule object with test values."""
    return Keys(fake_api_call)


@pytest.fixture(scope="function", name="fake_key")
def fake_key_fixture(fake_api_call: ApiCall) -> Key:
    """Return a Key object with test values."""
    return Key(fake_api_call, 1)
