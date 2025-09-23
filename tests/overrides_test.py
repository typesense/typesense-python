"""Tests for the Overrides class."""

from __future__ import annotations

import requests_mock
import pytest

from tests.utils.object_assertions import (
    assert_match_object,
    assert_object_lists_match,
    assert_to_contain_object,
)
from typesense.api_call import ApiCall
from typesense.collections import Collections
from typesense.overrides import OverrideRetrieveSchema, Overrides, OverrideSchema
from tests.utils.version import is_v30_or_above
from typesense.client import Client

pytestmark = pytest.mark.skipif(
    is_v30_or_above(
        Client({
            "api_key": "xyz",
            "nodes": [{"host": "localhost", "port": 8108, "protocol": "http"}],
        })
    ),
    reason="Run override tests only on less than v30",
)

def test_init(fake_api_call: ApiCall) -> None:
    """Test that the Overrides object is initialized correctly."""
    overrides = Overrides(fake_api_call, "companies")

    assert_match_object(overrides.api_call, fake_api_call)
    assert_object_lists_match(
        overrides.api_call.node_manager.nodes,
        fake_api_call.node_manager.nodes,
    )
    assert_match_object(
        overrides.api_call.config.nearest_node,
        fake_api_call.config.nearest_node,
    )

    assert not overrides.overrides


def test_get_missing_override(fake_overrides: Overrides) -> None:
    """Test that the Overrides object can get a missing override."""
    override = fake_overrides["company_override"]

    assert override.override_id == "company_override"
    assert_match_object(override.api_call, fake_overrides.api_call)
    assert_object_lists_match(
        override.api_call.node_manager.nodes, fake_overrides.api_call.node_manager.nodes
    )
    assert_match_object(
        override.api_call.config.nearest_node,
        fake_overrides.api_call.config.nearest_node,
    )
    assert override.collection_name == "companies"
    assert (
        override._endpoint_path()  # noqa: WPS437
        == "/collections/companies/overrides/company_override"
    )


def test_get_existing_override(fake_overrides: Overrides) -> None:
    """Test that the Overrides object can get an existing override."""
    override = fake_overrides["companies"]
    fetched_override = fake_overrides["companies"]

    assert len(fake_overrides.overrides) == 1

    assert override is fetched_override


def test_retrieve(fake_overrides: Overrides) -> None:
    """Test that the Overrides object can retrieve overrides."""
    json_response: OverrideRetrieveSchema = {
        "overrides": [
            {
                "id": "company_override",
                "rule": {"match": "exact", "query": "companies"},
            },
        ],
    }
    with requests_mock.Mocker() as mock:
        mock.get(
            "http://nearest:8108/collections/companies/overrides/",
            json=json_response,
        )

        response = fake_overrides.retrieve()

    assert len(response) == 1
    assert response["overrides"][0] == {
        "id": "company_override",
        "rule": {"match": "exact", "query": "companies"},
    }
    assert response == json_response


def test_create(fake_overrides: Overrides) -> None:
    """Test that the Overrides object can create a override."""
    json_response: OverrideSchema = {
        "id": "company_override",
        "rule": {"match": "exact", "query": "companies"},
    }

    with requests_mock.Mocker() as mock:
        mock.put(
            "http://nearest:8108/collections/companies/overrides/company_override",
            json=json_response,
        )

        fake_overrides.upsert(
            "company_override",
            {"rule": {"match": "exact", "query": "companies"}},
        )

        assert mock.call_count == 1
        assert mock.called is True
        assert mock.last_request.method == "PUT"
        assert (
            mock.last_request.url
            == "http://nearest:8108/collections/companies/overrides/company_override"
        )
        assert mock.last_request.json() == {
            "rule": {"match": "exact", "query": "companies"},
        }


def test_actual_create(
    actual_overrides: Overrides,
    delete_all: None,
    create_collection: None,
) -> None:
    """Test that the Overrides object can create an override on Typesense Server."""
    response = actual_overrides.upsert(
        "company_override",
        {
            "rule": {"match": "exact", "query": "companies"},
            "filter_by": "num_employees>10",
        },
    )

    assert response == {
        "id": "company_override",
        "rule": {"match": "exact", "query": "companies"},
        "filter_by": "num_employees>10",
    }


def test_actual_update(
    actual_overrides: Overrides,
    delete_all: None,
    create_collection: None,
) -> None:
    """Test that the Overrides object can update an override on Typesense Server."""
    create_response = actual_overrides.upsert(
        "company_override",
        {
            "rule": {"match": "exact", "query": "companies"},
            "filter_by": "num_employees>10",
        },
    )

    assert create_response == {
        "id": "company_override",
        "rule": {"match": "exact", "query": "companies"},
        "filter_by": "num_employees>10",
    }

    update_response = actual_overrides.upsert(
        "company_override",
        {
            "rule": {"match": "contains", "query": "companies"},
            "filter_by": "num_employees>20",
        },
    )

    assert update_response == {
        "id": "company_override",
        "rule": {"match": "contains", "query": "companies"},
        "filter_by": "num_employees>20",
    }


def test_actual_retrieve(
    delete_all: None,
    create_override: None,
    actual_collections: Collections,
) -> None:
    """Test that the Overrides object can retrieve an override from Typesense Server."""
    response = actual_collections["companies"].overrides.retrieve()

    assert len(response["overrides"]) == 1
    assert_to_contain_object(
        response["overrides"][0],
        {
            "id": "company_override",
            "rule": {"match": "exact", "query": "companies"},
            "filter_by": "num_employees>10",
        },
    )
