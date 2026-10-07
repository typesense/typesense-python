"""Tests for the Overrides class."""


import pytest

from tests.utils.object_assertions import (
    assert_match_object,
    assert_object_lists_match,
    assert_to_contain_object,
)
from typesense.sync.api_call import ApiCall
from typesense.async_.api_call import AsyncApiCall
from typesense.async_.collections import AsyncCollections
from typesense.sync.collections import Collections
from typesense.sync.overrides import Overrides
from tests.utils.version import is_v30_or_above
from typesense.sync.client import Client

pytestmark = pytest.mark.skipif(
    is_v30_or_above(
        Client(
            {
                "api_key": "xyz",
                "nodes": [{"host": "localhost", "port": 8108, "protocol": "http"}],
            }
        )
    ),
    reason="Run override tests only on less than v30",
)


def test_init(fake_api_call: ApiCall) -> None:
    """Test that the Overrides object is initialized correctly."""
    overrides = Overrides(fake_api_call, "companies")

    assert_match_object(overrides.api_call, fake_api_call)
    assert_object_lists_match(
        overrides.api_call.node_manager.nodes,
        fake_api_call.node_manager.nodes,
    )
    assert_match_object(
        overrides.api_call.config.nearest_node,
        fake_api_call.config.nearest_node,
    )

    assert not overrides.overrides


def test_get_missing_override(fake_overrides: Overrides) -> None:
    """Test that the Overrides object can get a missing override."""
    override = fake_overrides["company_override"]

    assert override.override_id == "company_override"
    assert_match_object(override.api_call, fake_overrides.api_call)
    assert_object_lists_match(
        override.api_call.node_manager.nodes, fake_overrides.api_call.node_manager.nodes
    )
    assert_match_object(
        override.api_call.config.nearest_node,
        fake_overrides.api_call.config.nearest_node,
    )
    assert override.collection_name == "companies"
    assert (
        override._endpoint_path  # noqa: WPS437
        == "/collections/companies/overrides/company_override"
    )


def test_get_existing_override(fake_overrides: Overrides) -> None:
    """Test that the Overrides object can get an existing override."""
    override = fake_overrides["companies"]
    fetched_override = fake_overrides["companies"]

    assert len(fake_overrides.overrides) == 1

    assert override is fetched_override


def test_actual_create(
    actual_overrides: Overrides,
    delete_all: None,
    create_collection: None,
) -> None:
    """Test that the Overrides object can create an override on Typesense Server."""
    response = actual_overrides.upsert(
        "company_override",
        {
            "rule": {"match": "exact", "query": "companies"},
            "filter_by": "num_employees>10",
        },
    )

    assert response == {
        "id": "company_override",
        "rule": {"match": "exact", "query": "companies"},
        "filter_by": "num_employees>10",
    }


def test_actual_update(
    actual_overrides: Overrides,
    delete_all: None,
    create_collection: None,
) -> None:
    """Test that the Overrides object can update an override on Typesense Server."""
    create_response = actual_overrides.upsert(
        "company_override",
        {
            "rule": {"match": "exact", "query": "companies"},
            "filter_by": "num_employees>10",
        },
    )

    assert create_response == {
        "id": "company_override",
        "rule": {"match": "exact", "query": "companies"},
        "filter_by": "num_employees>10",
    }

    update_response = actual_overrides.upsert(
        "company_override",
        {
            "rule": {"match": "contains", "query": "companies"},
            "filter_by": "num_employees>20",
        },
    )

    assert update_response == {
        "id": "company_override",
        "rule": {"match": "contains", "query": "companies"},
        "filter_by": "num_employees>20",
    }


def test_actual_retrieve(
    delete_all: None,
    create_override: None,
    actual_collections: Collections,
) -> None:
    """Test that the Overrides object can retrieve an override from Typesense Server."""
    response = actual_collections["companies"].overrides.retrieve()

    assert len(response["overrides"]) == 1
    assert_to_contain_object(
        response["overrides"][0],
        {
            "id": "company_override",
            "rule": {"match": "exact", "query": "companies"},
            "filter_by": "num_employees>10",
        },
    )


def test_init_async(fake_async_api_call: AsyncApiCall) -> None:
    """Test that the AsyncOverrides object is initialized correctly."""
    from typesense.async_.overrides import AsyncOverrides

    overrides = AsyncOverrides(fake_async_api_call, "companies")

    assert_match_object(overrides.api_call, fake_async_api_call)
    assert_object_lists_match(
        overrides.api_call.node_manager.nodes,
        fake_async_api_call.node_manager.nodes,
    )
    assert_match_object(
        overrides.api_call.config.nearest_node,
        fake_async_api_call.config.nearest_node,
    )

    assert not overrides.overrides


def test_get_missing_override_async(fake_async_overrides) -> None:
    """Test that the AsyncOverrides object can get a missing override."""

    override = fake_async_overrides["company_override"]

    assert override.override_id == "company_override"
    assert_match_object(override.api_call, fake_async_overrides.api_call)
    assert_object_lists_match(
        override.api_call.node_manager.nodes, fake_async_overrides.api_call.node_manager.nodes
    )
    assert_match_object(
        override.api_call.config.nearest_node,
        fake_async_overrides.api_call.config.nearest_node,
    )
    assert override.collection_name == "companies"
    assert (
        override._endpoint_path  # noqa: WPS437
        == "/collections/companies/overrides/company_override"
    )


def test_get_existing_override_async(fake_async_overrides) -> None:
    """Test that the AsyncOverrides object can get an existing override."""
    override = fake_async_overrides["companies"]
    fetched_override = fake_async_overrides["companies"]

    assert len(fake_async_overrides.overrides) == 1

    assert override is fetched_override


async def test_actual_create_async(
    actual_async_overrides,
    delete_all: None,
    create_collection: None,
) -> None:
    """Test that the AsyncOverrides object can create an override on Typesense Server."""
    response = await actual_async_overrides.upsert(
        "company_override",
        {
            "rule": {"match": "exact", "query": "companies"},
            "filter_by": "num_employees>10",
        },
    )

    assert response == {
        "id": "company_override",
        "rule": {"match": "exact", "query": "companies"},
        "filter_by": "num_employees>10",
    }


async def test_actual_update_async(
    actual_async_overrides,
    delete_all: None,
    create_collection: None,
) -> None:
    """Test that the AsyncOverrides object can update an override on Typesense Server."""
    create_response = await actual_async_overrides.upsert(
        "company_override",
        {
            "rule": {"match": "exact", "query": "companies"},
            "filter_by": "num_employees>10",
        },
    )

    assert create_response == {
        "id": "company_override",
        "rule": {"match": "exact", "query": "companies"},
        "filter_by": "num_employees>10",
    }

    update_response = await actual_async_overrides.upsert(
        "company_override",
        {
            "rule": {"match": "contains", "query": "companies"},
            "filter_by": "num_employees>20",
        },
    )

    assert update_response == {
        "id": "company_override",
        "rule": {"match": "contains", "query": "companies"},
        "filter_by": "num_employees>20",
    }


async def test_actual_retrieve_async(
    delete_all: None,
    create_override: None,
    actual_async_collections: AsyncCollections,
) -> None:
    """Test that the AsyncOverrides object can retrieve an override from Typesense Server."""
    response = await actual_async_collections["companies"].overrides.retrieve()

    assert len(response["overrides"]) == 1
    assert_to_contain_object(
        response["overrides"][0],
        {
            "id": "company_override",
            "rule": {"match": "exact", "query": "companies"},
            "filter_by": "num_employees>10",
        },
    )
