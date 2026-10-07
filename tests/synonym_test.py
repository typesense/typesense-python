"""Tests for the Synonym class."""

import pytest

from tests.utils.object_assertions import (
    assert_match_object,
    assert_object_lists_match,
    assert_to_contain_object,
)
from tests.utils.version import is_v30_or_above
from typesense.sync.api_call import ApiCall
from typesense.async_.api_call import AsyncApiCall
from typesense.async_.collections import AsyncCollections
from typesense.sync.collections import Collections
from typesense.sync.client import Client
from typesense.sync.synonym import Synonym


pytestmark = pytest.mark.skipif(
    is_v30_or_above(
        Client(
            {
                "api_key": "xyz",
                "nodes": [{"host": "localhost", "port": 8108, "protocol": "http"}],
            }
        )
    ),
    reason="Skip synonym tests on v30+",
)


def test_init(fake_api_call: ApiCall) -> None:
    """Test that the Synonym object is initialized correctly."""
    synonym = Synonym(fake_api_call, "companies", "company_synonym")

    assert synonym.collection_name == "companies"
    assert synonym.synonym_id == "company_synonym"
    assert_match_object(synonym.api_call, fake_api_call)
    assert_object_lists_match(
        synonym.api_call.node_manager.nodes,
        fake_api_call.node_manager.nodes,
    )
    assert_match_object(
        synonym.api_call.config.nearest_node,
        fake_api_call.config.nearest_node,
    )
    assert (
        synonym._endpoint_path  # noqa: WPS437
        == "/collections/companies/synonyms/company_synonym"
    )


def test_actual_retrieve(
    actual_collections: Collections,
    delete_all: None,
    create_synonym: None,
) -> None:
    """Test that the Synonym object can retrieve an synonym from Typesense Server."""
    response = actual_collections["companies"].synonyms["company_synonym"].retrieve()

    assert response["id"] == "company_synonym"

    assert response["synonyms"] == ["companies", "corporations", "firms"]
    assert_to_contain_object(
        response,
        {
            "id": "company_synonym",
            "synonyms": ["companies", "corporations", "firms"],
        },
    )


def test_actual_delete(
    actual_collections: Collections,
    delete_all: None,
    create_synonym: None,
) -> None:
    """Test that the Synonym object can delete an synonym from Typesense Server."""
    response = actual_collections["companies"].synonyms["company_synonym"].delete()

    assert response == {"id": "company_synonym"}


def test_init_async(fake_async_api_call: AsyncApiCall) -> None:
    """Test that the AsyncSynonym object is initialized correctly."""
    from typesense.async_.synonym import AsyncSynonym

    synonym = AsyncSynonym(fake_async_api_call, "companies", "company_synonym")

    assert synonym.collection_name == "companies"
    assert synonym.synonym_id == "company_synonym"
    assert_match_object(synonym.api_call, fake_async_api_call)
    assert_object_lists_match(
        synonym.api_call.node_manager.nodes,
        fake_async_api_call.node_manager.nodes,
    )
    assert_match_object(
        synonym.api_call.config.nearest_node,
        fake_async_api_call.config.nearest_node,
    )
    assert (
        synonym._endpoint_path  # noqa: WPS437
        == "/collections/companies/synonyms/company_synonym"
    )


async def test_actual_retrieve_async(
    actual_async_collections: AsyncCollections,
    delete_all: None,
    create_synonym: None,
) -> None:
    """Test that the AsyncSynonym object can retrieve an synonym from Typesense Server."""
    response = (
        await actual_async_collections["companies"]
        .synonyms["company_synonym"]
        .retrieve()
    )

    assert response["id"] == "company_synonym"

    assert response["synonyms"] == ["companies", "corporations", "firms"]
    assert_to_contain_object(
        response,
        {
            "id": "company_synonym",
            "synonyms": ["companies", "corporations", "firms"],
        },
    )


async def test_actual_delete_async(
    actual_async_collections: AsyncCollections,
    delete_all: None,
    create_synonym: None,
) -> None:
    """Test that the AsyncSynonym object can delete an synonym from Typesense Server."""
    response = (
        await actual_async_collections["companies"].synonyms["company_synonym"].delete()
    )

    assert response == {"id": "company_synonym"}
