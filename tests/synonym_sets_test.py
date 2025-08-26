"""Tests for the SynonymSets class."""

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
from typesense.synonym_sets import SynonymSets
from typesense.types.synonym_set import (
    SynonymSetCreateSchema,
    SynonymSetSchema,
)


pytestmark = pytest.mark.skipif(
    not is_v30_or_above(
        Client(
            {
                "api_key": "xyz",
                "nodes": [
                    {"host": "localhost", "port": 8108, "protocol": "http"}
                ],
            }
        )
    ),
    reason="Run synonym sets tests only on v30+",
)


def test_init(fake_api_call: ApiCall) -> None:
    """Test that the SynonymSets object is initialized correctly."""
    synsets = SynonymSets(fake_api_call)

    assert_match_object(synsets.api_call, fake_api_call)
    assert_object_lists_match(
        synsets.api_call.node_manager.nodes,
        fake_api_call.node_manager.nodes,
    )
    assert_match_object(
        synsets.api_call.config.nearest_node,
        fake_api_call.config.nearest_node,
    )


def test_retrieve(fake_synonym_sets: SynonymSets) -> None:
    """Test that the SynonymSets object can retrieve synonym sets."""
    json_response = [
        {
            "name": "test-set",
            "items": [
                {
                    "id": "company_synonym",
                    "root": "",
                    "synonyms": ["companies", "corporations", "firms"],
                }
            ],
        }
    ]

    with requests_mock.Mocker() as mock:
        mock.get(
            "http://nearest:8108/synonym_sets",
            json=json_response,
        )

        response = fake_synonym_sets.retrieve()

        assert isinstance(response, list)
        assert len(response) == 1
        assert response == json_response


def test_create(fake_synonym_sets: SynonymSets) -> None:
    """Test that the SynonymSets object can create a synonym set."""
    json_response: SynonymSetSchema = {
        "name": "test-set",
        "items": [
            {
                "id": "company_synonym",
                "synonyms": ["companies", "corporations", "firms"],
            }
        ],
    }

    with requests_mock.Mocker() as mock:
        mock.put(
            "http://nearest:8108/synonym_sets/test-set",
            json=json_response,
        )

        payload: SynonymSetCreateSchema = {
            "items": [
                {
                    "id": "company_synonym",
                    "synonyms": ["companies", "corporations", "firms"],
                }
            ]
        }
        fake_synonym_sets.upsert("test-set", payload)

        assert mock.call_count == 1
        assert mock.called is True
        assert mock.last_request.method == "PUT"
        assert (
            mock.last_request.url == "http://nearest:8108/synonym_sets/test-set"
        )
        assert mock.last_request.json() == payload


def test_actual_create(
    actual_synonym_sets: SynonymSets,
    delete_all_synonym_sets: None,
) -> None:
    """Test that the SynonymSets object can create a synonym set on Typesense Server."""
    response = actual_synonym_sets.upsert(
        "test-set",
        {
            "items": [
                {
                    "id": "company_synonym",
                    "synonyms": ["companies", "corporations", "firms"],
                }
            ]
        },
    )

    assert response == {
        "name": "test-set",
        "items": [
            {
                "id": "company_synonym",
                "root": "",
                "synonyms": ["companies", "corporations", "firms"],
            }
        ],
    }


def test_actual_retrieve(
    actual_synonym_sets: SynonymSets,
    delete_all_synonym_sets: None,
    create_synonym_set: None,
) -> None:
    """Test that the SynonymSets object can retrieve a synonym set from Typesense Server."""
    response = actual_synonym_sets.retrieve()

    assert isinstance(response, list)
    assert_to_contain_object(
        response[0],
        {
            "name": "test-set",
        },
    )


