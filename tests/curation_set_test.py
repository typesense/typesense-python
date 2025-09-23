"""Tests for the CurationSet class including items APIs."""

from __future__ import annotations

import pytest
import requests_mock

from tests.utils.version import is_v30_or_above
from typesense.client import Client
from typesense.curation_set import CurationSet
from typesense.types.curation_set import (
    CurationItemDeleteSchema,
    CurationItemSchema,
    CurationSetDeleteSchema,
    CurationSetListItemResponseSchema,
    CurationSetSchema,
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
    reason="Run curation set tests only on v30+",
)


def test_paths(fake_curation_set: CurationSet) -> None:
    assert fake_curation_set._endpoint_path == "/curation_sets/products"  # noqa: WPS437
    assert fake_curation_set._items_path == "/curation_sets/products/items"  # noqa: WPS437


def test_retrieve(fake_curation_set: CurationSet) -> None:
    json_response: CurationSetSchema = {
        "name": "products",
        "items": [],
    }
    with requests_mock.Mocker() as mock:
        mock.get(
            "/curation_sets/products",
            json=json_response,
        )
        res = fake_curation_set.retrieve()
        assert res == json_response


def test_delete(fake_curation_set: CurationSet) -> None:
    json_response: CurationSetDeleteSchema = {"name": "products"}
    with requests_mock.Mocker() as mock:
        mock.delete(
            "/curation_sets/products",
            json=json_response,
        )
        res = fake_curation_set.delete()
        assert res == json_response


def test_list_items(fake_curation_set: CurationSet) -> None:
    json_response: CurationSetListItemResponseSchema = [
        {
            "id": "rule-1",
            "rule": {"query": "shoe", "match": "contains"},
            "includes": [{"id": "123", "position": 1}],
        }
    ]
    with requests_mock.Mocker() as mock:
        mock.get(
            "/curation_sets/products/items?limit=10&offset=0",
            json=json_response,
        )
        res = fake_curation_set.list_items(limit=10, offset=0)
        assert res == json_response


def test_get_item(fake_curation_set: CurationSet) -> None:
    json_response: CurationItemSchema = {
        "id": "rule-1",
        "rule": {"query": "shoe", "match": "contains"},
        "includes": [{"id": "123", "position": 1}],
    }
    with requests_mock.Mocker() as mock:
        mock.get(
            "/curation_sets/products/items/rule-1",
            json=json_response,
        )
        res = fake_curation_set.get_item("rule-1")
        assert res == json_response


def test_upsert_item(fake_curation_set: CurationSet) -> None:
    payload: CurationItemSchema = {
        "id": "rule-1",
        "rule": {"query": "shoe", "match": "contains"},
        "includes": [{"id": "123", "position": 1}],
    }
    json_response = payload
    with requests_mock.Mocker() as mock:
        mock.put(
            "/curation_sets/products/items/rule-1",
            json=json_response,
        )
        res = fake_curation_set.upsert_item("rule-1", payload)
        assert res == json_response


def test_delete_item(fake_curation_set: CurationSet) -> None:
    json_response: CurationItemDeleteSchema = {"id": "rule-1"}
    with requests_mock.Mocker() as mock:
        mock.delete(
            "/curation_sets/products/items/rule-1",
            json=json_response,
        )
        res = fake_curation_set.delete_item("rule-1")
        assert res == json_response


