"""Tests for the Collection class."""

from __future__ import annotations

import time

import requests_mock

from tests.utils.object_assertions import (
    assert_match_object,
    assert_object_lists_match,
    assert_to_contain_object,
)
from typesense.api_call import ApiCall
from typesense.collection import Collection
from typesense.collections import Collections
from typesense.types.collection import CollectionSchema


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


def test_retrieve(fake_collection: Collection) -> None:
    """Test that the Collection object can retrieve a collection."""
    time_now = int(time.time())

    json_response: CollectionSchema = {
        "created_at": time_now,
        "default_sorting_field": "num_employees",
        "enable_nested_fields": False,
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
        "name": "companies",
        "num_documents": 0,
        "symbols_to_index": [],
        "token_separators": [],
        "synonym_sets": [],
        "curation_sets": [],
    }

    with requests_mock.mock() as mock:
        mock.get(
            "http://nearest:8108/collections/companies",
            json=json_response,
        )

        response = fake_collection.retrieve()

        assert len(mock.request_history) == 1
        assert mock.request_history[0].method == "GET"
        assert (
            mock.request_history[0].url == "http://nearest:8108/collections/companies"
        )

        assert response == json_response


def test_update(fake_collection: Collection) -> None:
    """Test that the Collection object can update a collection."""
    json_response: CollectionSchema = {
        "created_at": 1619711487,
        "default_sorting_field": "num_employees",
        "enable_nested_fields": False,
        "fields": [
            {
                "name": "company_name",
                "type": "string",
            },
            {
                "name": "num_employees",
                "type": "int32",
            },
            {
                "name": "num_locations",
                "type": "int32",
            },
        ],
        "name": "companies",
        "num_documents": 0,
        "symbols_to_index": [],
        "token_separators": [],
        "synonym_sets": [],
        "curation_sets": [],
    }

    with requests_mock.mock() as mock:
        mock.patch(
            "http://nearest:8108/collections/companies",
            json=json_response,
        )

        response = fake_collection.update(
            schema_change={
                "fields": [
                    {
                        "name": "num_locations",
                        "type": "int32",
                    },
                ],
            },
        )

        assert mock.call_count == 1
        assert mock.called is True
        assert mock.last_request.method == "PATCH"
        assert mock.last_request.url == "http://nearest:8108/collections/companies"
        assert mock.last_request.json() == {
            "fields": [
                {
                    "name": "num_locations",
                    "type": "int32",
                },
            ],
        }
        assert response == json_response


def test_delete(fake_collection: Collection) -> None:
    """Test that the Collection object can delete a collection."""
    json_response: CollectionSchema = {
        "created_at": 1619711487,
        "default_sorting_field": "num_employees",
        "enable_nested_fields": False,
        "fields": [
            {
                "name": "company_name",
                "type": "string",
            },
            {
                "name": "num_employees",
                "type": "int32",
            },
            {
                "name": "num_locations",
                "type": "int32",
            },
        ],
        "name": "companies",
        "num_documents": 0,
        "symbols_to_index": [],
        "token_separators": [],
        "synonym_sets": [],
        "curation_sets": [],
    }

    with requests_mock.mock() as mock:
        mock.delete(
            "http://nearest:8108/collections/companies",
            json=json_response,
        )

        response = fake_collection.delete()

        assert mock.call_count == 1
        assert mock.called is True
        assert mock.last_request.method == "DELETE"
        assert mock.last_request.url == "http://nearest:8108/collections/companies"
        assert response == json_response


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
        "synonym_sets": [],
        "curation_sets": [],
    }

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

    expected: CollectionSchema = {
        "fields": [
            {
                "name": "num_locations",
                "type": "int32",
            },
        ],
    }

    assert_to_contain_object(response.get("fields")[0], expected.get("fields")[0])
