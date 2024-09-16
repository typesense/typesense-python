"""Tests for the Override class."""

from __future__ import annotations

import requests_mock

from tests.utils.object_assertions import (
    assert_match_object,
    assert_object_lists_match,
    assert_to_contain_object,
)
from typesense.api_call import ApiCall
from typesense.collections import Collections
from typesense.override import Override, OverrideDeleteSchema
from typesense.types.override import OverrideSchema


def test_init(fake_api_call: ApiCall) -> None:
    """Test that the Override object is initialized correctly."""
    override = Override(fake_api_call, "companies", "company_override")

    assert override.collection_name == "companies"
    assert override.override_id == "company_override"
    assert_match_object(override.api_call, fake_api_call)
    assert_object_lists_match(
        override.api_call.node_manager.nodes,
        fake_api_call.node_manager.nodes,
    )
    assert_match_object(
        override.api_call.config.nearest_node,
        fake_api_call.config.nearest_node,
    )
    assert (
        override._endpoint_path()  # noqa: WPS437
        == "/collections/companies/overrides/company_override"
    )


def test_retrieve(fake_override: Override) -> None:
    """Test that the Override object can retrieve an override."""
    json_response: OverrideSchema = {
        "rule": {
            "match": "contains",
            "query": "companies",
        },
        "filter_by": "num_employees>10",
    }

    with requests_mock.Mocker() as mock:
        mock.get(
            "/collections/companies/overrides/company_override",
            json=json_response,
        )

        response = fake_override.retrieve()

        assert len(mock.request_history) == 1
        assert mock.request_history[0].method == "GET"
        assert (
            mock.request_history[0].url
            == "http://nearest:8108/collections/companies/overrides/company_override"
        )
        assert response == json_response


def test_delete(fake_override: Override) -> None:
    """Test that the Override object can delete an override."""
    json_response: OverrideDeleteSchema = {
        "id": "company_override",
    }
    with requests_mock.Mocker() as mock:
        mock.delete(
            "/collections/companies/overrides/company_override",
            json=json_response,
        )

        response = fake_override.delete()

        assert len(mock.request_history) == 1
        assert mock.request_history[0].method == "DELETE"
        assert (
            mock.request_history[0].url
            == "http://nearest:8108/collections/companies/overrides/company_override"
        )
        assert response == {"id": "company_override"}


def test_actual_retrieve(
    actual_collections: Collections,
    delete_all: None,
    create_override: None,
) -> None:
    """Test that the Override object can retrieve an override from Typesense Server."""
    response = actual_collections["companies"].overrides["company_override"].retrieve()

    assert response["rule"] == {
        "match": "exact",
        "query": "companies",
    }
    assert response["filter_by"] == "num_employees>10"
    assert_to_contain_object(
        response,
        {
            "rule": {
                "match": "exact",
                "query": "companies",
            },
            "filter_by": "num_employees>10",
        },
    )


def test_actual_delete(
    actual_collections: Collections,
    delete_all: None,
    create_override: None,
) -> None:
    """Test that the Override object can delete an override from Typesense Server."""
    response = actual_collections["companies"].overrides["company_override"].delete()

    assert response == {"id": "company_override"}
