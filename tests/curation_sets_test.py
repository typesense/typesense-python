"""Tests for the CurationSets class."""

from __future__ import annotations

import pytest
import requests_mock

from tests.utils.object_assertions import (
    assert_match_object,
    assert_object_lists_match,
    assert_to_contain_object,
)
from tests.utils.version import is_v30_or_above
from typesense.api_call import ApiCall
from typesense.client import Client
from typesense.curation_sets import CurationSets
from typesense.types.curation_set import CurationSetSchema, CurationSetUpsertSchema

pytestmark = pytest.mark.skipif(
    not is_v30_or_above(
        Client(
            {
                "api_key": "xyz",
                "nodes": [{"host": "localhost", "port": 8108, "protocol": "http"}],
            }
        )
    ),
    reason="Run curation sets tests only on v30+",
)


def test_init(fake_api_call: ApiCall) -> None:
    """Test that the CurationSets object is initialized correctly."""
    cur_sets = CurationSets(fake_api_call)

    assert_match_object(cur_sets.api_call, fake_api_call)
    assert_object_lists_match(
        cur_sets.api_call.node_manager.nodes,
        fake_api_call.node_manager.nodes,
    )


def test_retrieve(fake_curation_sets: CurationSets) -> None:
    """Test that the CurationSets object can retrieve curation sets."""
    json_response = [
        {
            "name": "products",
            "items": [
                {
                    "id": "rule-1",
                    "rule": {"query": "shoe", "match": "contains"},
                    "includes": [{"id": "123", "position": 1}],
                }
            ],
        }
    ]

    with requests_mock.Mocker() as mock:
        mock.get(
            "http://nearest:8108/curation_sets",
            json=json_response,
        )

        response = fake_curation_sets.retrieve()

        assert isinstance(response, list)
        assert len(response) == 1
        assert response == json_response


def test_upsert(fake_curation_sets: CurationSets) -> None:
    """Test that the CurationSets object can upsert a curation set."""
    json_response: CurationSetSchema = {
        "name": "products",
        "items": [
            {
                "id": "rule-1",
                "rule": {"query": "shoe", "match": "contains"},
                "includes": [{"id": "123", "position": 1}],
            }
        ],
    }

    with requests_mock.Mocker() as mock:
        mock.put(
            "http://nearest:8108/curation_sets/products",
            json=json_response,
        )

        payload: CurationSetUpsertSchema = {
            "items": [
                {
                    "id": "rule-1",
                    "rule": {"query": "shoe", "match": "contains"},
                    "includes": [{"id": "123", "position": 1}],
                }
            ]
        }
        response = fake_curation_sets.upsert("products", payload)

        assert response == json_response
        assert mock.call_count == 1
        assert mock.called is True
        assert mock.last_request.method == "PUT"
        assert mock.last_request.url == "http://nearest:8108/curation_sets/products"
        assert mock.last_request.json() == payload


def test_actual_upsert(
    actual_curation_sets: CurationSets,
    delete_all_curation_sets: None,
) -> None:
    """Test that the CurationSets object can upsert a curation set on Typesense Server."""
    response = actual_curation_sets.upsert(
        "products",
        {
            "items": [
                {
                    "id": "rule-1",
                    "rule": {"query": "shoe", "match": "contains"},
                    "includes": [{"id": "123", "position": 1}],
                    "excludes": [{"id": "999"}],
                }
            ]
        },
    )

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
                },
                "stop_processing": True,
            },
        ],
        "name": "products",
    }


def test_actual_retrieve(
    actual_curation_sets: CurationSets,
    delete_all_curation_sets: None,
    create_curation_set: None,
) -> None:
    """Test that the CurationSets object can retrieve curation sets from Typesense Server."""
    response = actual_curation_sets.retrieve()

    assert isinstance(response, list)
    assert_to_contain_object(
        response[0],
        {
            "name": "products",
        },
    )
