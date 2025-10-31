"""Tests for the Synonyms class."""

from __future__ import annotations

import pytest
import requests_mock

from tests.utils.object_assertions import (
    assert_match_object,
    assert_object_lists_match,
    assert_to_contain_object,
)
from typesense.api_call import ApiCall
from typesense.collections import Collections
from tests.utils.version import is_v30_or_above
from typesense.client import Client
from typesense.synonyms import Synonyms, SynonymSchema, SynonymsRetrieveSchema


pytestmark = pytest.mark.skipif(
    is_v30_or_above(
        Client(
            {
                "api_key": "xyz",
                "nodes": [{"host": "localhost", "port": 8108, "protocol": "http"}],
            }
        )
    ),
    reason="Skip synonyms tests on v30+",
)


def test_init(fake_api_call: ApiCall) -> None:
    """Test that the Synonyms object is initialized correctly."""
    synonyms = Synonyms(fake_api_call, "companies")

    assert_match_object(synonyms.api_call, fake_api_call)
    assert_object_lists_match(
        synonyms.api_call.node_manager.nodes,
        fake_api_call.node_manager.nodes,
    )
    assert_match_object(
        synonyms.api_call.config.nearest_node,
        fake_api_call.config.nearest_node,
    )

    assert not synonyms.synonyms


def test_get_missing_synonym(fake_synonyms: Synonyms) -> None:
    """Test that the Synonyms object can get a missing synonym."""
    synonym = fake_synonyms["company_synonym"]

    assert synonym.synonym_id == "company_synonym"
    assert_match_object(synonym.api_call, fake_synonyms.api_call)
    assert_object_lists_match(
        synonym.api_call.node_manager.nodes, fake_synonyms.api_call.node_manager.nodes
    )
    assert_match_object(
        synonym.api_call.config.nearest_node,
        fake_synonyms.api_call.config.nearest_node,
    )
    assert synonym.collection_name == "companies"
    assert (
        synonym._endpoint_path()  # noqa: WPS437
        == "/collections/companies/synonyms/company_synonym"
    )


def test_get_existing_synonym(fake_synonyms: Synonyms) -> None:
    """Test that the Synonyms object can get an existing synonym."""
    synonym = fake_synonyms["companies"]
    fetched_synonym = fake_synonyms["companies"]

    assert len(fake_synonyms.synonyms) == 1

    assert synonym is fetched_synonym


def test_retrieve(fake_synonyms: Synonyms) -> None:
    """Test that the Synonyms object can retrieve synonyms."""
    json_response: SynonymsRetrieveSchema = {
        "synonyms": [
            {
                "id": "company_synonym",
                "synonyms": ["companies", "corporations", "firms"],
            },
        ],
    }

    with requests_mock.Mocker() as mock:
        mock.get(
            "http://nearest:8108/collections/companies/synonyms/",
            json=json_response,
        )

        response = fake_synonyms.retrieve()

        assert len(response) == 1
        assert response["synonyms"][0] == {
            "id": "company_synonym",
            "synonyms": ["companies", "corporations", "firms"],
        }
        assert response == json_response


def test_create(fake_synonyms: Synonyms) -> None:
    """Test that the Synonyms object can create a synonym."""
    json_response: SynonymSchema = {
        "id": "company_synonym",
        "synonyms": ["companies", "corporations", "firms"],
    }

    with requests_mock.Mocker() as mock:
        mock.put(
            "http://nearest:8108/collections/companies/synonyms/company_synonym",
            json=json_response,
        )

        fake_synonyms.upsert(
            "company_synonym",
            {"synonyms": ["companies", "corporations", "firms"]},
        )

        assert mock.call_count == 1
        assert mock.called is True
        assert mock.last_request.method == "PUT"
        assert (
            mock.last_request.url
            == "http://nearest:8108/collections/companies/synonyms/company_synonym"
        )
        assert mock.last_request.json() == {
            "synonyms": ["companies", "corporations", "firms"],
        }


def test_actual_create(
    actual_synonyms: Synonyms,
    delete_all: None,
    create_collection: None,
) -> None:
    """Test that the Synonyms object can create an synonym on Typesense Server."""
    response = actual_synonyms.upsert(
        "company_synonym",
        {"synonyms": ["companies", "corporations", "firms"]},
    )

    assert response == {
        "id": "company_synonym",
        "synonyms": ["companies", "corporations", "firms"],
    }


def test_actual_update(
    actual_synonyms: Synonyms,
    delete_all: None,
    create_collection: None,
) -> None:
    """Test that the Synonyms object can update an synonym on Typesense Server."""
    create_response = actual_synonyms.upsert(
        "company_synonym",
        {"synonyms": ["companies", "corporations", "firms"]},
    )

    assert create_response == {
        "id": "company_synonym",
        "synonyms": ["companies", "corporations", "firms"],
    }

    update_response = actual_synonyms.upsert(
        "company_synonym",
        {"synonyms": ["companies", "corporations"]},
    )

    assert update_response == {
        "id": "company_synonym",
        "synonyms": ["companies", "corporations"],
    }


def test_actual_retrieve(
    delete_all: None,
    create_synonym: None,
    actual_collections: Collections,
) -> None:
    """Test that the Synonyms object can retrieve an synonym from Typesense Server."""
    response = actual_collections["companies"].synonyms.retrieve()

    assert len(response["synonyms"]) == 1
    assert_to_contain_object(
        response["synonyms"][0],
        {
            "id": "company_synonym",
            "synonyms": ["companies", "corporations", "firms"],
        },
    )
