"""Tests for the Aliases class."""

from __future__ import annotations

import requests_mock

from tests.utils.object_assertions import (
    assert_match_object,
    assert_object_lists_match,
    assert_to_contain_object,
)
from typesense.aliases import Aliases
from typesense.api_call import ApiCall
from typesense.types.alias import AliasesResponseSchema, AliasSchema


def test_init(fake_api_call: ApiCall) -> None:
    """Test that the Aliases object is initialized correctly."""
    aliases = Aliases(fake_api_call)

    assert_match_object(aliases.api_call, fake_api_call)
    assert_object_lists_match(
        aliases.api_call.node_manager.nodes,
        fake_api_call.node_manager.nodes,
    )
    assert_match_object(
        aliases.api_call.config.nearest_node,
        fake_api_call.config.nearest_node,
    )

    assert not aliases.aliases


def test_get_missing_alias(fake_aliases: Aliases) -> None:
    """Test that the Aliases object can get a missing alias."""
    alias = fake_aliases["company_alias"]

    assert alias.name == "company_alias"
    assert_match_object(alias.api_call, fake_aliases.api_call)
    assert_object_lists_match(
        alias.api_call.node_manager.nodes, fake_aliases.api_call.node_manager.nodes
    )
    assert_match_object(
        alias.api_call.config.nearest_node,
        fake_aliases.api_call.config.nearest_node,
    )
    assert alias._endpoint_path == "/aliases/company_alias"  # noqa: WPS437


def test_get_existing_alias(fake_aliases: Aliases) -> None:
    """Test that the Aliases object can get an existing alias."""
    alias = fake_aliases["companies"]
    fetched_alias = fake_aliases["companies"]

    assert len(fake_aliases.aliases) == 1

    assert alias is fetched_alias


def test_retrieve(fake_aliases: Aliases) -> None:
    """Test that the Aliases object can retrieve aliases."""
    json_response: AliasesResponseSchema = {
        "aliases": [
            {
                "collection_name": "companies",
                "name": "company_alias",
            },
        ],
    }

    with requests_mock.Mocker() as mock:
        mock.get(
            "http://nearest:8108/aliases",
            json=json_response,
        )

        response = fake_aliases.retrieve()

        assert len(response) == 1
        assert response["aliases"][0] == {
            "collection_name": "companies",
            "name": "company_alias",
        }
        assert response == json_response


def test_create(fake_aliases: Aliases) -> None:
    """Test that the Aliases object can create a alias."""
    json_response: AliasSchema = {
        "collection_name": "companies",
        "name": "company_alias",
    }

    with requests_mock.Mocker() as mock:
        mock.put(
            "http://nearest:8108/aliases/company_alias",
            json=json_response,
        )

        fake_aliases.upsert(
            "company_alias",
            {"collection_name": "companies", "name": "company_alias"},
        )

        assert mock.call_count == 1
        assert mock.called is True
        assert mock.last_request.method == "PUT"
        assert mock.last_request.url == "http://nearest:8108/aliases/company_alias"
        assert mock.last_request.json() == json_response


def test_actual_create(actual_aliases: Aliases, delete_all_aliases: None) -> None:
    """Test that the Aliases object can create an alias on Typesense Server."""
    response = actual_aliases.upsert("company_alias", {"collection_name": "companies"})

    assert response == {"collection_name": "companies", "name": "company_alias"}


def test_actual_update(
    actual_aliases: Aliases,
    delete_all_aliases: None,
    delete_all: None,
    create_collection: None,
    create_another_collection: None,
) -> None:
    """Test that the Aliases object can update an alias on Typesense Server."""
    create_response = actual_aliases.upsert(
        "company_alias",
        {"collection_name": "companies"},
    )

    assert create_response == {"collection_name": "companies", "name": "company_alias"}

    update_response = actual_aliases.upsert(
        "company_alias",
        {"collection_name": "companies_2"},
    )

    assert update_response == {
        "collection_name": "companies_2",
        "name": "company_alias",
    }


def test_actual_retrieve(
    delete_all: None,
    delete_all_aliases: None,
    create_alias: None,
    actual_aliases: Aliases,
) -> None:
    """Test that the Aliases object can retrieve an alias from Typesense Server."""
    response = actual_aliases.retrieve()

    assert len(response["aliases"]) == 1
    assert_to_contain_object(
        response["aliases"][0],
        {
            "collection_name": "companies",
            "name": "company_alias",
        },
    )
