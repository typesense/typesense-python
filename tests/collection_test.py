"""Tests for the Collection class."""

from tests.utils.object_assertions import (
    assert_match_object,
    assert_object_lists_match,
    assert_to_contain_object,
)
from tests.utils.version import is_v30_or_above
from typesense.sync.api_call import ApiCall
from typesense.sync.client import Client
from typesense.sync.collection import Collection
from typesense.sync.collections import Collections
from typesense.types.collection import CollectionSchema


is_v30_or_above_server = is_v30_or_above(
    Client(
        {
            "api_key": "xyz",
            "nodes": [{"host": "localhost", "port": 8108, "protocol": "http"}],
        }
    )
)


def test_init(fake_api_call: ApiCall) -> None:
    """Test that the Collection object is initialized correctly."""
    collection = Collection(fake_api_call, "companies")

    assert collection.name == "companies"
    assert_match_object(collection.api_call, fake_api_call)
    assert_object_lists_match(
        collection.api_call.node_manager.nodes,
        fake_api_call.node_manager.nodes,
    )
    assert_match_object(
        collection.api_call.config.nearest_node,
        fake_api_call.config.nearest_node,
    )
    assert collection.overrides.collection_name == "companies"
    assert collection._endpoint_path == "/collections/companies"  # noqa: WPS437


def test_actual_retrieve(
    actual_collections: Collections,
    delete_all: None,
    create_collection: None,
) -> None:
    """Test that the Collection object can retrieve a collection."""
    response = actual_collections["companies"].retrieve()

    expected: CollectionSchema = {
        "default_sorting_field": "num_employees",
        "enable_nested_fields": False,
        "fields": [
            {
                "name": "company_name",
                "type": "string",
                "facet": False,
                "index": True,
                "optional": False,
                "locale": "",
                "sort": False,
                "infix": False,
                "stem": False,
                "stem_dictionary": "",
                "store": True,
            },
            {
                "name": "num_employees",
                "type": "int32",
                "facet": False,
                "index": True,
                "optional": False,
                "locale": "",
                "sort": True,
                "infix": False,
                "stem": False,
                "stem_dictionary": "",
                "store": True,
            },
        ],
        "name": "companies",
        "num_documents": 0,
        "symbols_to_index": [],
        "token_separators": [],
    }
    if is_v30_or_above_server:
        expected["synonym_sets"] = []
        expected["curation_sets"] = []
        expected["fields"][0]["truncate_len"] = 100
        expected["fields"][1]["truncate_len"] = 100

    response.pop("created_at")

    assert response == expected


def test_actual_update(
    actual_collections: Collections,
    delete_all: None,
    create_collection: None,
) -> None:
    """Test that the Collection object can update a collection."""
    response = actual_collections["companies"].update(
        {"fields": [{"name": "num_locations", "type": "int32"}]},
    )

    expected_field = {"name": "num_locations", "type": "int32"}
    if is_v30_or_above_server:
        expected_field["truncate_len"] = 100

    assert_to_contain_object(response.get("fields")[0], expected_field)
