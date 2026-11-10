"""Tests for SynonymSet item-level APIs."""


import pytest

from tests.utils.version import is_v30_or_above
from typesense.async_.synonym_set import AsyncSynonymSet
from typesense.async_.synonym_sets import AsyncSynonymSets
from typesense.sync.client import Client
from typesense.sync.synonym_set import SynonymSet
from typesense.sync.synonym_sets import SynonymSets
from typesense.types.synonym_set import (
    SynonymItemSchema,
    SynonymItemUpsertSchema,
)

pytestmark = pytest.mark.skipif(
    not is_v30_or_above(
        Client(
            {
                "api_key": "xyz",
                "nodes": [{"host": "localhost", "port": 8108, "protocol": "http"}],
            }
        )
    ),
    reason="Run synonym set items tests only on v30+",
)


def test_items_paths(fake_synonym_set: SynonymSet) -> None:
    items = fake_synonym_set.items
    assert items._endpoint_path == "/synonym_sets/test-set/items"  # noqa: WPS437
    assert (
        items["company_synonym"]._endpoint_path  # noqa: WPS437
        == "/synonym_sets/test-set/items/company_synonym"
    )


def test_items_paths_async(fake_async_synonym_set: AsyncSynonymSet) -> None:
    items = fake_async_synonym_set.items
    assert items._endpoint_path == "/synonym_sets/test-set/items"  # noqa: WPS437
    assert (
        items["company_synonym"]._endpoint_path  # noqa: WPS437
        == "/synonym_sets/test-set/items/company_synonym"
    )


def test_actual_list_items(
    actual_synonym_sets: SynonymSets,
    delete_all_synonym_sets: None,
    create_synonym_set: None,
) -> None:
    """Test that the SynonymSet object can list items from Typesense Server."""
    response = actual_synonym_sets["test-set"].list_items()

    assert response == [
        {
            "id": "company_synonym",
            "root": "",
            "synonyms": ["companies", "corporations", "firms"],
        },
    ]


def test_actual_get_item(
    actual_synonym_sets: SynonymSets,
    delete_all_synonym_sets: None,
    create_synonym_set: None,
) -> None:
    """Test that the SynonymSet object can get a specific item from Typesense Server."""
    response = actual_synonym_sets["test-set"].get_item("company_synonym")

    assert response == {
        "id": "company_synonym",
        "root": "",
        "synonyms": ["companies", "corporations", "firms"],
    }


def test_actual_upsert_item(
    actual_synonym_sets: SynonymSets,
    delete_all_synonym_sets: None,
    create_synonym_set: None,
) -> None:
    """Test that the SynonymSet object can upsert an item in Typesense Server."""
    payload: SynonymItemSchema = {
        "id": "brand_synonym",
        "synonyms": ["brand", "brands", "label"],
    }
    response = actual_synonym_sets["test-set"].upsert_item("brand_synonym", payload)

    assert response == {
        "id": "brand_synonym",
        "synonyms": ["brand", "brands", "label"],
    }


def test_actual_delete_item(
    actual_synonym_sets: SynonymSets,
    delete_all_synonym_sets: None,
    create_synonym_set: None,
) -> None:
    """Test that the SynonymSet object can delete an item from Typesense Server."""
    response = actual_synonym_sets["test-set"].delete_item("company_synonym")

    assert response == {"id": "company_synonym"}


async def test_actual_list_items_async(
    actual_async_synonym_sets: AsyncSynonymSets,
    delete_all_synonym_sets: None,
    create_synonym_set: None,
) -> None:
    """Test that the AsyncSynonymSet object can list items from Typesense Server."""
    response = await actual_async_synonym_sets["test-set"].list_items()

    assert response == [
        {
            "id": "company_synonym",
            "root": "",
            "synonyms": ["companies", "corporations", "firms"],
        },
    ]


async def test_actual_get_item_async(
    actual_async_synonym_sets: AsyncSynonymSets,
    delete_all_synonym_sets: None,
    create_synonym_set: None,
) -> None:
    """Test that the AsyncSynonymSet object can get a specific item from Typesense Server."""
    response = await actual_async_synonym_sets["test-set"].get_item("company_synonym")

    assert response == {
        "id": "company_synonym",
        "root": "",
        "synonyms": ["companies", "corporations", "firms"],
    }


async def test_actual_upsert_item_async(
    actual_async_synonym_sets: AsyncSynonymSets,
    delete_all_synonym_sets: None,
    create_synonym_set: None,
) -> None:
    """Test that the AsyncSynonymSet object can upsert an item in Typesense Server."""
    payload: SynonymItemSchema = {
        "id": "brand_synonym",
        "synonyms": ["brand", "brands", "label"],
    }
    response = await actual_async_synonym_sets["test-set"].upsert_item(
        "brand_synonym", payload
    )

    assert response == {
        "id": "brand_synonym",
        "synonyms": ["brand", "brands", "label"],
    }


async def test_actual_delete_item_async(
    actual_async_synonym_sets: AsyncSynonymSets,
    delete_all_synonym_sets: None,
    create_synonym_set: None,
) -> None:
    """Test that the AsyncSynonymSet object can delete an item from Typesense Server."""
    response = await actual_async_synonym_sets["test-set"].delete_item(
        "company_synonym"
    )

    assert response == {"id": "company_synonym"}


def test_actual_items_retrieve(
    actual_synonym_sets: SynonymSets,
    delete_all_synonym_sets: None,
    create_synonym_set: None,
) -> None:
    """Test that the SynonymSetItems object can list items from Typesense Server."""
    response = actual_synonym_sets["test-set"].items.retrieve()

    assert response == [
        {
            "id": "company_synonym",
            "root": "",
            "synonyms": ["companies", "corporations", "firms"],
        },
    ]


def test_actual_items_retrieve_paginated(
    actual_synonym_sets: SynonymSets,
    delete_all_synonym_sets: None,
    create_synonym_set: None,
) -> None:
    """Test that the SynonymSetItems object can paginate items from Typesense Server."""
    items = actual_synonym_sets["test-set"].items
    items.upsert("brand_synonym", {"synonyms": ["brand", "brands", "label"]})
    response = items.retrieve(limit=1, offset=1)

    assert response == [
        {
            "id": "brand_synonym",
            "root": "",
            "synonyms": ["brand", "brands", "label"],
        },
    ]


def test_actual_items_upsert(
    actual_synonym_sets: SynonymSets,
    delete_all_synonym_sets: None,
    create_synonym_set: None,
) -> None:
    """Test that the SynonymSetItems object can upsert an item in Typesense Server."""
    payload: SynonymItemUpsertSchema = {"synonyms": ["brand", "brands", "label"]}
    response = actual_synonym_sets["test-set"].items.upsert("brand_synonym", payload)

    assert response == {
        "id": "brand_synonym",
        "synonyms": ["brand", "brands", "label"],
    }


def test_actual_item_retrieve(
    actual_synonym_sets: SynonymSets,
    delete_all_synonym_sets: None,
    create_synonym_set: None,
) -> None:
    """Test that the SynonymSetItem object can retrieve an item from Typesense Server."""
    response = actual_synonym_sets["test-set"].items["company_synonym"].retrieve()

    assert response == {
        "id": "company_synonym",
        "root": "",
        "synonyms": ["companies", "corporations", "firms"],
    }


def test_actual_item_upsert(
    actual_synonym_sets: SynonymSets,
    delete_all_synonym_sets: None,
    create_synonym_set: None,
) -> None:
    """Test that the SynonymSetItem object can upsert an item in Typesense Server."""
    payload: SynonymItemUpsertSchema = {"synonyms": ["brand", "brands", "label"]}
    response = actual_synonym_sets["test-set"].items["brand_synonym"].upsert(payload)

    assert response == {
        "id": "brand_synonym",
        "synonyms": ["brand", "brands", "label"],
    }


def test_actual_item_delete(
    actual_synonym_sets: SynonymSets,
    delete_all_synonym_sets: None,
    create_synonym_set: None,
) -> None:
    """Test that the SynonymSetItem object can delete an item from Typesense Server."""
    response = actual_synonym_sets["test-set"].items["company_synonym"].delete()

    assert response == {"id": "company_synonym"}


async def test_actual_items_retrieve_async(
    actual_async_synonym_sets: AsyncSynonymSets,
    delete_all_synonym_sets: None,
    create_synonym_set: None,
) -> None:
    """Test that the AsyncSynonymSetItems object can list items from Typesense Server."""
    response = await actual_async_synonym_sets["test-set"].items.retrieve()

    assert response == [
        {
            "id": "company_synonym",
            "root": "",
            "synonyms": ["companies", "corporations", "firms"],
        },
    ]


async def test_actual_items_upsert_async(
    actual_async_synonym_sets: AsyncSynonymSets,
    delete_all_synonym_sets: None,
    create_synonym_set: None,
) -> None:
    """Test that the AsyncSynonymSetItems object can upsert an item in Typesense Server."""
    payload: SynonymItemUpsertSchema = {"synonyms": ["brand", "brands", "label"]}
    response = await actual_async_synonym_sets["test-set"].items.upsert(
        "brand_synonym", payload
    )

    assert response == {
        "id": "brand_synonym",
        "synonyms": ["brand", "brands", "label"],
    }


async def test_actual_item_retrieve_async(
    actual_async_synonym_sets: AsyncSynonymSets,
    delete_all_synonym_sets: None,
    create_synonym_set: None,
) -> None:
    """Test that the AsyncSynonymSetItem object can retrieve an item from Typesense Server."""
    response = (
        await actual_async_synonym_sets["test-set"].items["company_synonym"].retrieve()
    )

    assert response == {
        "id": "company_synonym",
        "root": "",
        "synonyms": ["companies", "corporations", "firms"],
    }


async def test_actual_item_upsert_async(
    actual_async_synonym_sets: AsyncSynonymSets,
    delete_all_synonym_sets: None,
    create_synonym_set: None,
) -> None:
    """Test that the AsyncSynonymSetItem object can upsert an item in Typesense Server."""
    payload: SynonymItemUpsertSchema = {"synonyms": ["brand", "brands", "label"]}
    response = (
        await actual_async_synonym_sets["test-set"].items["brand_synonym"].upsert(payload)
    )

    assert response == {
        "id": "brand_synonym",
        "synonyms": ["brand", "brands", "label"],
    }


async def test_actual_item_delete_async(
    actual_async_synonym_sets: AsyncSynonymSets,
    delete_all_synonym_sets: None,
    create_synonym_set: None,
) -> None:
    """Test that the AsyncSynonymSetItem object can delete an item from Typesense Server."""
    response = (
        await actual_async_synonym_sets["test-set"].items["company_synonym"].delete()
    )

    assert response == {"id": "company_synonym"}
