"""Fixtures for alias tests."""

import pytest
import requests

from typesense.alias import Alias
from typesense.aliases import Aliases
from typesense.api_call import ApiCall


@pytest.fixture(scope="function", name="delete_all_aliases")
def clear_typesense_aliases() -> None:
    """Remove all aliases from the Typesense server."""
    url = "http://localhost:8108/aliases"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}

    # Get the list of collections
    response = requests.get(url, headers=headers, timeout=3)
    response.raise_for_status()

    aliases = response.json()

    # Delete each alias
    for alias in aliases["aliases"]:
        alias_name = alias.get("name")
        delete_url = f"{url}/{alias_name}"
        delete_response = requests.delete(delete_url, headers=headers, timeout=3)
        delete_response.raise_for_status()


@pytest.fixture(scope="function", name="create_alias")
def create_alias_fixture(create_collection: None) -> None:
    """Create an alias in the Typesense server."""
    url = "http://localhost:8108/aliases/company_alias"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}
    alias_data = {
        "collection_name": "companies",
    }

    alias_creation_response = requests.put(
        url,
        headers=headers,
        json=alias_data,
        timeout=3,
    )
    alias_creation_response.raise_for_status()


@pytest.fixture(scope="function", name="actual_aliases")
def actual_aliases_fixture(actual_api_call: ApiCall) -> Aliases:
    """Return a Aliases object using a real API."""
    return Aliases(actual_api_call)


@pytest.fixture(scope="function", name="fake_aliases")
def fake_aliases_fixture(fake_api_call: ApiCall) -> Aliases:
    """Return a Aliases object with test values."""
    return Aliases(fake_api_call)


@pytest.fixture(scope="function", name="fake_alias")
def fake_alias_fixture(fake_api_call: ApiCall) -> Alias:
    """Return a Alias object with test values."""
    return Alias(fake_api_call, "company_alias")
