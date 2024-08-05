"""Pytest configuration file."""

import pytest
import requests

from typesense.api_call import ApiCall
from typesense.collection import Collection
from typesense.collections import Collections
from typesense.configuration import Configuration
from typesense.override import Override
from typesense.overrides import Overrides
from typesense.synonym import Synonym
from typesense.synonyms import Synonyms

pytest.register_assert_rewrite("utils.object_assertions")


@pytest.fixture(scope="function", name="delete_all")
def clear_typesense_collections() -> None:
    """Remove all collections from the Typesense server."""
    url = "http://localhost:8108/collections"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}

    # Get the list of collections
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    collections = response.json()

    # Delete each collection
    for collection in collections:
        collection_name = collection["name"]
        delete_url = f"{url}/{collection_name}"
        delete_response = requests.delete(delete_url, headers=headers)
        delete_response.raise_for_status()


@pytest.fixture(scope="function", name="create_collection")
def create_collection_fixture() -> None:
    """Create a collection in the Typesense server."""
    url = "http://localhost:8108/collections"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}
    data = {
        "name": "companies",
        "fields": [
            {
                "name": "company_name",
                "type": "string",
            },
            {
                "name": "num_employees",
                "type": "int32",
            },
        ],
        "default_sorting_field": "num_employees",
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()


@pytest.fixture(scope="function", name="create_override")
def create_override_fixture(create_collection: None) -> None:
    url = "http://localhost:8108/collections/companies/overrides/company_override"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}
    data = {
        "rule": {"match": "exact", "query": "companies"},
        "filter_by": "num_employees>10",
    }

    response = requests.put(url, headers=headers, json=data)
    response.raise_for_status()


@pytest.fixture(scope="function", name="create_synonym")
def create_synonym_fixture(create_collection: None) -> None:
    url = "http://localhost:8108/collections/companies/synonyms/company_synonym"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}
    data = {
        "synonyms": ["companies", "corporations", "firms"],
    }

    response = requests.put(url, headers=headers, json=data)
    response.raise_for_status()


@pytest.fixture(scope="function", name="actual_config")
def actual_config_fixture() -> Configuration:
    return Configuration(
        config_dict={
            "api_key": "xyz",
            "nodes": [
                {
                    "host": "localhost",
                    "port": 8108,
                    "protocol": "http",
                }
            ],
        }
    )


@pytest.fixture(scope="function", name="actual_api_call")
def actual_api_call_fixture(actual_config: Configuration) -> ApiCall:
    return ApiCall(actual_config)


@pytest.fixture(scope="function", name="actual_collections")
def actual_collections_fixture(actual_api_call: ApiCall) -> Collections:
    return Collections(actual_api_call)


@pytest.fixture(scope="function", name="actual_overrides")
def actual_overrides_fixture(actual_api_call: ApiCall) -> Overrides:
    return Overrides(actual_api_call, "companies")


@pytest.fixture(scope="function", name="actual_synonyms")
def actual_synonyms_fixture(actual_api_call: ApiCall) -> Synonyms:
    return Synonyms(actual_api_call, "companies")


@pytest.fixture(scope="function", name="fake_config")
def fake_config_fixture() -> Configuration:
    """Return a Configuration object with test values."""
    return Configuration(
        config_dict={
            "api_key": "test-api-key",
            "nodes": [
                {
                    "host": "node0",
                    "port": 8108,
                    "protocol": "http",
                },
                {
                    "host": "node1",
                    "port": 8108,
                    "protocol": "http",
                },
                {
                    "host": "node2",
                    "port": 8108,
                    "protocol": "http",
                },
            ],
            "nearest_node": {
                "host": "nearest",
                "port": 8108,
                "protocol": "http",
            },
            "num_retries": 3,
            "healthcheck_interval_seconds": 60,
            "retry_interval_seconds": 0.001,
            "connection_timeout_seconds": 0.001,
            "verify": True,
        },
    )


@pytest.fixture(scope="function", name="fake_api_call")
def fake_api_call_fixture(
    fake_config: Configuration,
) -> ApiCall:
    """Return an ApiCall object with test values."""
    return ApiCall(fake_config)


@pytest.fixture(scope="function", name="fake_collections")
def fake_collections_fixture(fake_api_call: ApiCall) -> Collections:
    """Return a Collection object with test values."""
    return Collections(fake_api_call)


@pytest.fixture(scope="function", name="fake_collection")
def fake_collection_fixture(fake_api_call: ApiCall) -> Collection:
    """Return a Collection object with test values."""
    return Collection(fake_api_call, "companies")


@pytest.fixture(scope="function", name="fake_overrides")
def fake_overrides_fixture(fake_api_call: ApiCall) -> Overrides:
    """Return a Collection object with test values."""
    return Overrides(fake_api_call, "companies")


@pytest.fixture(scope="function", name="fake_override")
def fake_override_fixture(fake_api_call: ApiCall) -> Override:
    """Return a Collection object with test values."""
    return Override(fake_api_call, "companies", "company_override")


@pytest.fixture(scope="function", name="fake_synonyms")
def fake_synonyms_fixture(fake_api_call: ApiCall) -> Synonyms:
    """Return a Collection object with test values."""
    return Synonyms(fake_api_call, "companies")


@pytest.fixture(scope="function", name="fake_synonym")
def fake_override_synonym(fake_api_call: ApiCall) -> Synonym:
    """Return a Collection object with test values."""
    return Synonym(fake_api_call, "companies", "company_synonym")
