"""Tests for the Collections class."""

from __future__ import annotations

import sys

import requests_mock

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

from tests.utils.object_assertions import assert_match_object, assert_object_lists_match
from typesense.api_call import ApiCall
from typesense.collections import Collections
from typesense.types.collection import CollectionSchema


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


def test_get_existing_collection(fake_collections: Collections) -> None:
    """Test that the Collections object can get an existing collection."""
    collection = fake_collections["companies"]
    fetched_collection = fake_collections["companies"]

    assert len(fake_collections.collections) == 1

    assert collection is fetched_collection


def test_retrieve(fake_collections: Collections) -> None:
    """Test that the Collections object can retrieve collections."""
    json_response: typing.List[CollectionSchema] = [
        {
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
        },
        {
            "created_at": 1619711488,
            "default_sorting_field": "likes",
            "enable_nested_fields": False,
            "fields": [
                {
                    "name": "name",
                    "type": "string",
                },
                {
                    "name": "likes",
                    "type": "int32",
                },
            ],
            "name": "posts",
            "num_documents": 0,
            "symbols_to_index": [],
            "token_separators": [],
            "synonym_sets": [],
        },
    ]
    with requests_mock.Mocker() as mock:
        mock.get("http://nearest:8108/collections", json=json_response)

        response = fake_collections.retrieve()

    assert len(response) == 2
    assert response[0]["name"] == "companies"
    assert response[1]["name"] == "posts"
    assert response == json_response


def test_create(fake_collections: Collections) -> None:
    """Test that the Collections object can create a collection."""
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
        ],
        "name": "companies",
        "num_documents": 0,
        "symbols_to_index": [],
        "token_separators": [],
        "synonym_sets": [],
    }

    with requests_mock.Mocker() as mock:
        mock.post(
            "http://nearest:8108/collections",
            json=json_response,
        )

        fake_collections.create(
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
                    },
                ],
                "default_sorting_field": "num_employees",
            },
        )

        assert mock.call_count == 1
        assert mock.called is True
        assert mock.last_request.method == "POST"
        assert mock.last_request.url == "http://nearest:8108/collections"
        assert mock.last_request.json() == {
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


def test_actual_create(actual_collections: Collections, delete_all: None) -> None:
    """Test that the Collections object can create a collection on Typesense Server."""
    expected: CollectionSchema = {
        "default_sorting_field": "",
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
                "truncate_len": 100,
                "store": True,
            },
            {
                "name": "num_employees",
                "type": "int32",
                "facet": False,
                "index": True,
                "optional": False,
                "locale": "",
                "sort": False,
                "infix": False,
                "stem": False,
                "stem_dictionary": "",
                "truncate_len": 100,
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
        {
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
                    "truncate_len": 100,
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
                    "truncate_len": 100,
                    "store": True,
                },
            ],
            "name": "companies",
            "num_documents": 0,
            "symbols_to_index": [],
            "token_separators": [],
            "synonym_sets": [],
            "curation_sets": [],
        },
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
