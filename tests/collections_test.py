"""Tests for the Collections class."""

import sys

from typesense.async_.api_call import AsyncApiCall


if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

from tests.utils.object_assertions import assert_match_object, assert_object_lists_match
from typesense.sync.api_call import ApiCall
from tests.utils.version import is_v30_or_above
from typesense.sync.collections import Collections
from typesense.async_.collections import AsyncCollections
from typesense.sync.client import Client
from typesense.types.collection import CollectionSchema


IS_V30_OR_ABOVE = is_v30_or_above(
    Client(
        {
            "api_key": "xyz",
            "nodes": [{"host": "localhost", "port": 8108, "protocol": "http"}],
        }
    )
)


def expected_collection_field(
    name: str,
    type_: str,
    *,
    sort: bool,
) -> dict[str, typing.Any]:
    field: dict[str, typing.Any] = {
        "name": name,
        "type": type_,
        "facet": False,
        "index": True,
        "optional": False,
        "locale": "",
        "sort": sort,
        "infix": False,
        "stem": False,
        "stem_dictionary": "",
        "store": True,
    }
    if IS_V30_OR_ABOVE:
        field["truncate_len"] = 100
    return field


def expected_collection_schema(
    *,
    default_sorting_field: str,
    fields: typing.List[dict[str, typing.Any]],
    name: str,
) -> CollectionSchema:
    expected: CollectionSchema = {
        "default_sorting_field": default_sorting_field,
        "enable_nested_fields": False,
        "fields": fields,
        "name": name,
        "num_documents": 0,
        "symbols_to_index": [],
        "token_separators": [],
    }
    if IS_V30_OR_ABOVE:
        expected["synonym_sets"] = []
        expected["curation_sets"] = []
    return expected


def test_init(fake_api_call: ApiCall) -> None:
    """Test that the Collections object is initialized correctly."""
    collections = Collections(fake_api_call)

    assert_match_object(collections.api_call, fake_api_call)
    assert_object_lists_match(
        collections.api_call.node_manager.nodes,
        fake_api_call.node_manager.nodes,
    )
    assert_match_object(
        collections.api_call.config.nearest_node,
        fake_api_call.config.nearest_node,
    )
    assert not collections.collections


def test_init_async(fake_async_api_call: AsyncApiCall) -> None:
    """Test that the Collections object is initialized correctly."""
    collections = AsyncCollections(fake_async_api_call)

    assert_match_object(collections.api_call, fake_async_api_call)
    assert_object_lists_match(
        collections.api_call.node_manager.nodes,
        fake_async_api_call.node_manager.nodes,
    )
    assert_match_object(
        collections.api_call.config.nearest_node,
        fake_async_api_call.config.nearest_node,
    )
    assert not collections.collections


def test_get_missing_collection(fake_collections: Collections) -> None:
    """Test that the Collections object can get a missing collection."""
    collection = fake_collections["companies"]

    assert collection.name == "companies"
    assert_match_object(collection.api_call, fake_collections.api_call)
    assert_object_lists_match(
        collection.api_call.node_manager.nodes,
        fake_collections.api_call.node_manager.nodes,
    )
    assert_match_object(
        collection.api_call.config.nearest_node,
        fake_collections.api_call.config.nearest_node,
    )
    assert collection.overrides.collection_name == "companies"
    assert collection._endpoint_path == "/collections/companies"  # noqa: WPS437


def test_get_missing_collection_async(fake_async_collections: Collections) -> None:
    """Test that the Collections object can get a missing collection."""
    collection = fake_async_collections["companies"]

    assert collection.name == "companies"
    assert_match_object(collection.api_call, fake_async_collections.api_call)
    assert_object_lists_match(
        collection.api_call.node_manager.nodes,
        fake_async_collections.api_call.node_manager.nodes,
    )
    assert_match_object(
        collection.api_call.config.nearest_node,
        fake_async_collections.api_call.config.nearest_node,
    )
    assert collection.overrides.collection_name == "companies"
    assert collection._endpoint_path == "/collections/companies"  # noqa: WPS437


def test_get_existing_collection(fake_collections: Collections) -> None:
    """Test that the Collections object can get an existing collection."""
    collection = fake_collections["companies"]
    fetched_collection = fake_collections["companies"]

    assert len(fake_collections.collections) == 1

    assert collection is fetched_collection


def test_actual_create(actual_collections: Collections, delete_all: None) -> None:
    """Test that the Collections object can create a collection on Typesense Server."""
    expected = expected_collection_schema(
        default_sorting_field="",
        fields=[
            expected_collection_field("company_name", "string", sort=False),
            expected_collection_field("num_employees", "int32", sort=False),
        ],
        name="companies",
    )

    response = actual_collections.create(
        {
            "name": "companies",
            "fields": [
                {
                    "name": "company_name",
                    "type": "string",
                },
                {
                    "name": "num_employees",
                    "type": "int32",
                    "sort": False,
                },
            ],
        },
    )

    response.pop("created_at")

    assert response == expected


def test_actual_retrieve(
    actual_collections: Collections,
    delete_all: None,
    create_collection: None,
) -> None:
    """Test that the Collections object can retrieve collections."""
    response = actual_collections.retrieve()

    expected: typing.List[CollectionSchema] = [
        expected_collection_schema(
            default_sorting_field="num_employees",
            fields=[
                expected_collection_field("company_name", "string", sort=False),
                expected_collection_field("num_employees", "int32", sort=True),
            ],
            name="companies",
        ),
    ]

    response[0].pop("created_at")
    assert response == expected


def test_actual_contains(
    actual_collections: Collections,
    delete_all: None,
    create_collection: None,
) -> None:
    """Test that the Collections object can check if a collection exists in Typesense."""
    # Test for existing collection
    assert "companies" in actual_collections

    # Test for non-existing collection
    assert "non_existent_collection" not in actual_collections
    # Test again
    assert "non_existent_collection" not in actual_collections


async def test_actual_create_async(
    actual_async_collections: AsyncCollections, delete_all: None
) -> None:
    """Test that the Collections object can create a collection on Typesense Server."""
    expected = expected_collection_schema(
        default_sorting_field="",
        fields=[
            expected_collection_field("company_name", "string", sort=False),
            expected_collection_field("num_employees", "int32", sort=False),
        ],
        name="companies",
    )

    response = await actual_async_collections.create(
        {
            "name": "companies",
            "fields": [
                {
                    "name": "company_name",
                    "type": "string",
                },
                {
                    "name": "num_employees",
                    "type": "int32",
                    "sort": False,
                },
            ],
        },
    )

    response.pop("created_at")

    assert response == expected


async def test_actual_retrieve_async(
    actual_async_collections: AsyncCollections,
    delete_all: None,
    create_collection: None,
) -> None:
    """Test that the Collections object can retrieve collections."""
    response = await actual_async_collections.retrieve()

    expected: typing.List[CollectionSchema] = [
        expected_collection_schema(
            default_sorting_field="num_employees",
            fields=[
                expected_collection_field("company_name", "string", sort=False),
                expected_collection_field("num_employees", "int32", sort=True),
            ],
            name="companies",
        ),
    ]

    response[0].pop("created_at")
    assert response == expected
