"""Tests for the Override class."""


import pytest

from tests.utils.object_assertions import (
    assert_match_object,
    assert_object_lists_match,
    assert_to_contain_object,
)
from typesense.sync.api_call import ApiCall
from typesense.async_.api_call import AsyncApiCall
from typesense.async_.collections import AsyncCollections
from typesense.async_.override import AsyncOverride
from typesense.sync.collections import Collections
from typesense.sync.override import Override
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
    """Test that the Override object is initialized correctly."""
    override = Override(fake_api_call, "companies", "company_override")

    assert override.collection_name == "companies"
    assert override.override_id == "company_override"
    assert_match_object(override.api_call, fake_api_call)
    assert_object_lists_match(
        override.api_call.node_manager.nodes,
        fake_api_call.node_manager.nodes,
    )
    assert_match_object(
        override.api_call.config.nearest_node,
        fake_api_call.config.nearest_node,
    )
    assert (
        override._endpoint_path  # noqa: WPS437
        == "/collections/companies/overrides/company_override"
    )


def test_actual_retrieve(
    actual_collections: Collections,
    delete_all: None,
    create_override: None,
) -> None:
    """Test that the Override object can retrieve an override from Typesense Server."""
    response = actual_collections["companies"].overrides["company_override"].retrieve()

    assert response["rule"] == {
        "match": "exact",
        "query": "companies",
    }
    assert response["filter_by"] == "num_employees>10"
    assert_to_contain_object(
        response,
        {
            "rule": {
                "match": "exact",
                "query": "companies",
            },
            "filter_by": "num_employees>10",
        },
    )


def test_actual_delete(
    actual_collections: Collections,
    delete_all: None,
    create_override: None,
) -> None:
    """Test that the Override object can delete an override from Typesense Server."""
    response = actual_collections["companies"].overrides["company_override"].delete()

    assert response == {"id": "company_override"}


def test_init_async(fake_async_api_call: AsyncApiCall) -> None:
    """Test that the AsyncOverride object is initialized correctly."""
    override = AsyncOverride(fake_async_api_call, "companies", "company_override")

    assert override.collection_name == "companies"
    assert override.override_id == "company_override"
    assert_match_object(override.api_call, fake_async_api_call)
    assert_object_lists_match(
        override.api_call.node_manager.nodes,
        fake_async_api_call.node_manager.nodes,
    )
    assert_match_object(
        override.api_call.config.nearest_node,
        fake_async_api_call.config.nearest_node,
    )
    assert (
        override._endpoint_path  # noqa: WPS437
        == "/collections/companies/overrides/company_override"
    )


async def test_actual_retrieve_async(
    actual_async_collections: AsyncCollections,
    delete_all: None,
    create_override: None,
) -> None:
    """Test that the AsyncOverride object can retrieve an override from Typesense Server."""
    response = await actual_async_collections["companies"].overrides["company_override"].retrieve()

    assert response["rule"] == {
        "match": "exact",
        "query": "companies",
    }
    assert response["filter_by"] == "num_employees>10"
    assert_to_contain_object(
        response,
        {
            "rule": {
                "match": "exact",
                "query": "companies",
            },
            "filter_by": "num_employees>10",
        },
    )


async def test_actual_delete_async(
    actual_async_collections: AsyncCollections,
    delete_all: None,
    create_override: None,
) -> None:
    """Test that the AsyncOverride object can delete an override from Typesense Server."""
    response = await actual_async_collections["companies"].overrides["company_override"].delete()

    assert response == {"id": "company_override"}
