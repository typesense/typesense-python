"""Tests for SynonymSet item-level APIs."""

from __future__ import annotations

import pytest
import requests_mock

from tests.utils.version import is_v30_or_above
from typesense.client import Client
from typesense.synonym_set import SynonymSet
from typesense.types.synonym_set import (
    SynonymItemDeleteSchema,
    SynonymItemSchema,
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
    reason="Run synonym set items tests only on v30+",
)


def test_list_items(fake_synonym_set: SynonymSet) -> None:
    json_response = [
        {"id": "nike", "synonyms": ["nike", "nikes"]},
        {"id": "adidas", "synonyms": ["adidas", "adi"]},
    ]
    with requests_mock.Mocker() as mock:
        mock.get(
            "/synonym_sets/test-set/items?limit=10&offset=0",
            json=json_response,
        )
        res = fake_synonym_set.list_items(limit=10, offset=0)
        assert res == json_response


def test_get_item(fake_synonym_set: SynonymSet) -> None:
    json_response: SynonymItemSchema = {
        "id": "nike",
        "synonyms": ["nike", "nikes"],
    }
    with requests_mock.Mocker() as mock:
        mock.get(
            "/synonym_sets/test-set/items/nike",
            json=json_response,
        )
        res = fake_synonym_set.get_item("nike")
        assert res == json_response


def test_upsert_item(fake_synonym_set: SynonymSet) -> None:
    payload: SynonymItemSchema = {
        "id": "nike",
        "synonyms": ["nike", "nikes"],
    }
    json_response = payload
    with requests_mock.Mocker() as mock:
        mock.put(
            "/synonym_sets/test-set/items/nike",
            json=json_response,
        )
        res = fake_synonym_set.upsert_item("nike", payload)
        assert res == json_response


def test_delete_item(fake_synonym_set: SynonymSet) -> None:
    json_response: SynonymItemDeleteSchema = {"id": "nike"}
    with requests_mock.Mocker() as mock:
        mock.delete(
            "/synonym_sets/test-set/items/nike",
            json=json_response,
        )
        res = fake_synonym_set.delete_item("nike")
        assert res == json_response


