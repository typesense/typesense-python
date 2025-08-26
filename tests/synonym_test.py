"""Tests for the Synonym class."""

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
from typesense.collections import Collections
from typesense.client import Client
from typesense.synonym import Synonym, SynonymDeleteSchema
from typesense.synonyms import SynonymSchema


pytestmark = pytest.mark.skipif(
    is_v30_or_above(
        Client(
            {
                "api_key": "xyz",
                "nodes": [
                    {"host": "localhost", "port": 8108, "protocol": "http"}
                ],
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
        synonym._endpoint_path()  # noqa: WPS437
        == "/collections/companies/synonyms/company_synonym"
    )


def test_retrieve(fake_synonym: Synonym) -> None:
    """Test that the Synonym object can retrieve an synonym."""
    json_response: SynonymSchema = {
        "id": "company_synonym",
        "synonyms": ["companies", "corporations", "firms"],
    }

    with requests_mock.Mocker() as mock:
        mock.get(
            "/collections/companies/synonyms/company_synonym",
            json=json_response,
        )

        response = fake_synonym.retrieve()

        assert len(mock.request_history) == 1
        assert mock.request_history[0].method == "GET"
        assert (
            mock.request_history[0].url
            == "http://nearest:8108/collections/companies/synonyms/company_synonym"
        )
        assert response == json_response


def test_delete(fake_synonym: Synonym) -> None:
    """Test that the Synonym object can delete an synonym."""
    json_response: SynonymDeleteSchema = {
        "id": "company_synonym",
    }
    with requests_mock.Mocker() as mock:
        mock.delete(
            "/collections/companies/synonyms/company_synonym",
            json=json_response,
        )

        response = fake_synonym.delete()

        assert len(mock.request_history) == 1
        assert mock.request_history[0].method == "DELETE"
        assert (
            mock.request_history[0].url
            == "http://nearest:8108/collections/companies/synonyms/company_synonym"
        )
        assert response == {"id": "company_synonym"}


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
