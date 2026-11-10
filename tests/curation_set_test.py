"""Tests for the CurationSet class including items APIs."""

import pytest

from tests.utils.version import is_v30_or_above
from typesense.async_.curation_set import AsyncCurationSet
from typesense.async_.curation_sets import AsyncCurationSets
from typesense.sync.client import Client
from typesense.sync.curation_set import CurationSet
from typesense.sync.curation_sets import CurationSets
from typesense.types.curation_set import CurationItemCreateSchema, CurationItemSchema

pytestmark = pytest.mark.skipif(
    not is_v30_or_above(
        Client(
            {
                "api_key": "xyz",
                "nodes": [{"host": "localhost", "port": 8108, "protocol": "http"}],
            }
        )
    ),
    reason="Run curation set tests only on v30+",
)


def test_paths(fake_curation_set: CurationSet) -> None:
    assert fake_curation_set._endpoint_path == "/curation_sets/products"  # noqa: WPS437
    assert fake_curation_set.items._endpoint_path == "/curation_sets/products/items"  # noqa: WPS437
    assert (
        fake_curation_set.items["rule-1"]._endpoint_path  # noqa: WPS437
        == "/curation_sets/products/items/rule-1"
    )


def test_paths_async(fake_async_curation_set: AsyncCurationSet) -> None:
    assert fake_async_curation_set._endpoint_path == "/curation_sets/products"  # noqa: WPS437
    assert fake_async_curation_set.items._endpoint_path == "/curation_sets/products/items"  # noqa: WPS437
    assert (
        fake_async_curation_set.items["rule-1"]._endpoint_path  # noqa: WPS437
        == "/curation_sets/products/items/rule-1"
    )


def test_actual_retrieve(
    actual_curation_sets: CurationSets,
    delete_all_curation_sets: None,
    create_curation_set: None,
) -> None:
    """Test that the CurationSet object can retrieve a curation set from Typesense Server."""
    response = actual_curation_sets["products"].retrieve()

    assert response == {
        "items": [
            {
                "excludes": [
                    {
                        "id": "999",
                    },
                ],
                "filter_curated_hits": False,
                "id": "rule-1",
                "includes": [
                    {
                        "id": "123",
                        "position": 1,
                    },
                ],
                "remove_matched_tokens": False,
                "rule": {
                    "match": "contains",
                    "query": "shoe",
                    "stem": False,
                    "synonyms": False,
                },
                "stop_processing": True,
            },
        ],
        "name": "products",
    }


def test_actual_delete(
    actual_curation_sets: CurationSets,
    create_curation_set: None,
) -> None:
    """Test that the CurationSet object can delete a curation set from Typesense Server."""
    response = actual_curation_sets["products"].delete()

    print(response)
    assert response == {"name": "products"}


def test_actual_list_items(
    actual_curation_sets: CurationSets,
    delete_all_curation_sets: None,
    create_curation_set: None,
) -> None:
    """Test that the CurationSet object can list items from Typesense Server."""
    response = actual_curation_sets["products"].list_items()

    assert response == [
        {
            "excludes": [
                {
                    "id": "999",
                },
            ],
            "filter_curated_hits": False,
            "id": "rule-1",
            "includes": [
                {
                    "id": "123",
                    "position": 1,
                },
            ],
            "remove_matched_tokens": False,
            "rule": {
                "match": "contains",
                "query": "shoe",
                "stem": False,
                "synonyms": False,
            },
            "stop_processing": True,
        },
    ]


def test_actual_get_item(
    actual_curation_sets: CurationSets,
    delete_all_curation_sets: None,
    create_curation_set: None,
) -> None:
    """Test that the CurationSet object can get a specific item from Typesense Server."""
    response = actual_curation_sets["products"].get_item("rule-1")

    assert response == {
        "excludes": [
            {
                "id": "999",
            },
        ],
        "filter_curated_hits": False,
        "id": "rule-1",
        "includes": [
            {
                "id": "123",
                "position": 1,
            },
        ],
        "remove_matched_tokens": False,
        "rule": {
            "match": "contains",
            "query": "shoe",
            "stem": False,
            "synonyms": False,
        },
        "stop_processing": True,
    }


def test_actual_upsert_item(
    actual_curation_sets: CurationSets,
    delete_all_curation_sets: None,
    create_curation_set: None,
) -> None:
    """Test that the CurationSet object can upsert an item in Typesense Server."""
    payload: CurationItemSchema = {
        "id": "rule-2",
        "rule": {"query": "boot", "match": "exact"},
        "includes": [{"id": "456", "position": 2}],
        "excludes": [{"id": "888"}],
    }
    response = actual_curation_sets["products"].upsert_item("rule-2", payload)

    assert response == {
        "excludes": [
            {
                "id": "888",
            },
        ],
        "id": "rule-2",
        "includes": [
            {
                "id": "456",
                "position": 2,
            },
        ],
        "rule": {
            "match": "exact",
            "query": "boot",
        },
    }


def test_actual_delete_item(
    actual_curation_sets: CurationSets,
    delete_all_curation_sets: None,
    create_curation_set: None,
) -> None:
    """Test that the CurationSet object can delete an item from Typesense Server."""
    response = actual_curation_sets["products"].delete_item("rule-1")

    assert response == {"id": "rule-1"}


async def test_actual_retrieve_async(
    actual_async_curation_sets: AsyncCurationSets,
    delete_all_curation_sets: None,
    create_curation_set: None,
) -> None:
    """Test that the AsyncCurationSet object can retrieve a curation set from Typesense Server."""
    response = await actual_async_curation_sets["products"].retrieve()

    assert response == {
        "items": [
            {
                "excludes": [
                    {
                        "id": "999",
                    },
                ],
                "filter_curated_hits": False,
                "id": "rule-1",
                "includes": [
                    {
                        "id": "123",
                        "position": 1,
                    },
                ],
                "remove_matched_tokens": False,
                "rule": {
                    "match": "contains",
                    "query": "shoe",
                    "stem": False,
                    "synonyms": False,
                },
                "stop_processing": True,
            },
        ],
        "name": "products",
    }


async def test_actual_delete_async(
    actual_async_curation_sets: AsyncCurationSets,
    create_curation_set: None,
) -> None:
    """Test that the AsyncCurationSet object can delete a curation set from Typesense Server."""
    response = await actual_async_curation_sets["products"].delete()

    assert response == {"name": "products"}


async def test_actual_list_items_async(
    actual_async_curation_sets: AsyncCurationSets,
    delete_all_curation_sets: None,
    create_curation_set: None,
) -> None:
    """Test that the AsyncCurationSet object can list items from Typesense Server."""
    response = await actual_async_curation_sets["products"].list_items()

    assert response == [
        {
            "excludes": [
                {
                    "id": "999",
                },
            ],
            "filter_curated_hits": False,
            "id": "rule-1",
            "includes": [
                {
                    "id": "123",
                    "position": 1,
                },
            ],
            "remove_matched_tokens": False,
            "rule": {
                "match": "contains",
                "query": "shoe",
                "stem": False,
                "synonyms": False,
            },
            "stop_processing": True,
        },
    ]


async def test_actual_get_item_async(
    actual_async_curation_sets: AsyncCurationSets,
    delete_all_curation_sets: None,
    create_curation_set: None,
) -> None:
    """Test that the AsyncCurationSet object can get a specific item from Typesense Server."""
    response = await actual_async_curation_sets["products"].get_item("rule-1")

    assert response == {
        "excludes": [
            {
                "id": "999",
            },
        ],
        "filter_curated_hits": False,
        "id": "rule-1",
        "includes": [
            {
                "id": "123",
                "position": 1,
            },
        ],
        "remove_matched_tokens": False,
        "rule": {
            "match": "contains",
            "query": "shoe",
            "stem": False,
            "synonyms": False,
        },
        "stop_processing": True,
    }


async def test_actual_upsert_item_async(
    actual_async_curation_sets: AsyncCurationSets,
    delete_all_curation_sets: None,
    create_curation_set: None,
) -> None:
    """Test that the AsyncCurationSet object can upsert an item in Typesense Server."""
    payload: CurationItemSchema = {
        "id": "rule-2",
        "rule": {"query": "boot", "match": "exact"},
        "includes": [{"id": "456", "position": 2}],
        "excludes": [{"id": "888"}],
    }
    response = await actual_async_curation_sets["products"].upsert_item(
        "rule-2", payload
    )

    assert response == {
        "excludes": [
            {
                "id": "888",
            },
        ],
        "id": "rule-2",
        "includes": [
            {
                "id": "456",
                "position": 2,
            },
        ],
        "rule": {
            "match": "exact",
            "query": "boot",
        },
    }


async def test_actual_delete_item_async(
    actual_async_curation_sets: AsyncCurationSets,
    delete_all_curation_sets: None,
    create_curation_set: None,
) -> None:
    """Test that the AsyncCurationSet object can delete an item from Typesense Server."""
    response = await actual_async_curation_sets["products"].delete_item("rule-1")

    assert response == {"id": "rule-1"}


def test_actual_items_retrieve(
    actual_curation_sets: CurationSets,
    delete_all_curation_sets: None,
    create_curation_set: None,
) -> None:
    """Test that the CurationSetItems object can list items from Typesense Server."""
    response = actual_curation_sets["products"].items.retrieve()

    assert response == [
        {
            "excludes": [
                {
                    "id": "999",
                },
            ],
            "filter_curated_hits": False,
            "id": "rule-1",
            "includes": [
                {
                    "id": "123",
                    "position": 1,
                },
            ],
            "remove_matched_tokens": False,
            "rule": {
                "match": "contains",
                "query": "shoe",
                "stem": False,
                "synonyms": False,
            },
            "stop_processing": True,
        },
    ]


def test_actual_items_retrieve_paginated(
    actual_curation_sets: CurationSets,
    delete_all_curation_sets: None,
    create_curation_set: None,
) -> None:
    """Test that the CurationSetItems object can paginate items from Typesense Server."""
    items = actual_curation_sets["products"].items
    items.upsert("rule-2", {"rule": {"tags": ["boot"]}, "excludes": [{"id": "888"}]})
    response = items.retrieve(limit=1, offset=1)

    assert [item["id"] for item in response] == ["rule-2"]


def test_actual_items_upsert(
    actual_curation_sets: CurationSets,
    delete_all_curation_sets: None,
    create_curation_set: None,
) -> None:
    """Test that the CurationSetItems object can upsert an item in Typesense Server."""
    payload: CurationItemCreateSchema = {
        "rule": {"query": "boot", "match": "exact"},
        "includes": [{"id": "456", "position": 2}],
        "excludes": [{"id": "888"}],
    }
    response = actual_curation_sets["products"].items.upsert("rule-2", payload)

    assert response == {
        "excludes": [
            {
                "id": "888",
            },
        ],
        "id": "rule-2",
        "includes": [
            {
                "id": "456",
                "position": 2,
            },
        ],
        "rule": {
            "match": "exact",
            "query": "boot",
        },
    }


def test_actual_item_retrieve(
    actual_curation_sets: CurationSets,
    delete_all_curation_sets: None,
    create_curation_set: None,
) -> None:
    """Test that the CurationSetItem object can retrieve an item from Typesense Server."""
    response = actual_curation_sets["products"].items["rule-1"].retrieve()

    assert response == {
        "excludes": [
            {
                "id": "999",
            },
        ],
        "filter_curated_hits": False,
        "id": "rule-1",
        "includes": [
            {
                "id": "123",
                "position": 1,
            },
        ],
        "remove_matched_tokens": False,
        "rule": {
            "match": "contains",
            "query": "shoe",
            "stem": False,
            "synonyms": False,
        },
        "stop_processing": True,
    }


def test_actual_item_upsert(
    actual_curation_sets: CurationSets,
    delete_all_curation_sets: None,
    create_curation_set: None,
) -> None:
    """Test that the CurationSetItem object can upsert an item in Typesense Server."""
    payload: CurationItemCreateSchema = {
        "rule": {"query": "boot", "match": "exact"},
        "includes": [{"id": "456", "position": 2}],
        "excludes": [{"id": "888"}],
    }
    response = actual_curation_sets["products"].items["rule-2"].upsert(payload)

    assert response == {
        "excludes": [
            {
                "id": "888",
            },
        ],
        "id": "rule-2",
        "includes": [
            {
                "id": "456",
                "position": 2,
            },
        ],
        "rule": {
            "match": "exact",
            "query": "boot",
        },
    }


def test_actual_item_delete(
    actual_curation_sets: CurationSets,
    delete_all_curation_sets: None,
    create_curation_set: None,
) -> None:
    """Test that the CurationSetItem object can delete an item from Typesense Server."""
    response = actual_curation_sets["products"].items["rule-1"].delete()

    assert response == {"id": "rule-1"}


async def test_actual_items_retrieve_async(
    actual_async_curation_sets: AsyncCurationSets,
    delete_all_curation_sets: None,
    create_curation_set: None,
) -> None:
    """Test that the AsyncCurationSetItems object can list items from Typesense Server."""
    response = await actual_async_curation_sets["products"].items.retrieve()

    assert response == [
        {
            "excludes": [
                {
                    "id": "999",
                },
            ],
            "filter_curated_hits": False,
            "id": "rule-1",
            "includes": [
                {
                    "id": "123",
                    "position": 1,
                },
            ],
            "remove_matched_tokens": False,
            "rule": {
                "match": "contains",
                "query": "shoe",
                "stem": False,
                "synonyms": False,
            },
            "stop_processing": True,
        },
    ]


async def test_actual_items_upsert_async(
    actual_async_curation_sets: AsyncCurationSets,
    delete_all_curation_sets: None,
    create_curation_set: None,
) -> None:
    """Test that the AsyncCurationSetItems object can upsert an item in Typesense Server."""
    payload: CurationItemCreateSchema = {
        "rule": {"query": "boot", "match": "exact"},
        "includes": [{"id": "456", "position": 2}],
        "excludes": [{"id": "888"}],
    }
    response = (
        await actual_async_curation_sets["products"].items.upsert("rule-2", payload)
    )

    assert response == {
        "excludes": [
            {
                "id": "888",
            },
        ],
        "id": "rule-2",
        "includes": [
            {
                "id": "456",
                "position": 2,
            },
        ],
        "rule": {
            "match": "exact",
            "query": "boot",
        },
    }


async def test_actual_item_retrieve_async(
    actual_async_curation_sets: AsyncCurationSets,
    delete_all_curation_sets: None,
    create_curation_set: None,
) -> None:
    """Test that the AsyncCurationSetItem object can retrieve an item from Typesense Server."""
    response = await actual_async_curation_sets["products"].items["rule-1"].retrieve()

    assert response == {
        "excludes": [
            {
                "id": "999",
            },
        ],
        "filter_curated_hits": False,
        "id": "rule-1",
        "includes": [
            {
                "id": "123",
                "position": 1,
            },
        ],
        "remove_matched_tokens": False,
        "rule": {
            "match": "contains",
            "query": "shoe",
            "stem": False,
            "synonyms": False,
        },
        "stop_processing": True,
    }


async def test_actual_item_upsert_async(
    actual_async_curation_sets: AsyncCurationSets,
    delete_all_curation_sets: None,
    create_curation_set: None,
) -> None:
    """Test that the AsyncCurationSetItem object can upsert an item in Typesense Server."""
    payload: CurationItemCreateSchema = {
        "rule": {"query": "boot", "match": "exact"},
        "includes": [{"id": "456", "position": 2}],
        "excludes": [{"id": "888"}],
    }
    response = (
        await actual_async_curation_sets["products"].items["rule-2"].upsert(payload)
    )

    assert response == {
        "excludes": [
            {
                "id": "888",
            },
        ],
        "id": "rule-2",
        "includes": [
            {
                "id": "456",
                "position": 2,
            },
        ],
        "rule": {
            "match": "exact",
            "query": "boot",
        },
    }


async def test_actual_item_delete_async(
    actual_async_curation_sets: AsyncCurationSets,
    delete_all_curation_sets: None,
    create_curation_set: None,
) -> None:
    """Test that the AsyncCurationSetItem object can delete an item from Typesense Server."""
    response = await actual_async_curation_sets["products"].items["rule-1"].delete()

    assert response == {"id": "rule-1"}
