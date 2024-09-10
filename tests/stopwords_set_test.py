"""Tests for the StopwordsSet class."""

from __future__ import annotations

import requests_mock

from tests.utils.object_assertions import assert_match_object, assert_object_lists_match
from typesense.api_call import ApiCall
from typesense.stopwords import Stopwords
from typesense.stopwords_set import StopwordsSet
from typesense.types.stopword import StopwordDeleteSchema, StopwordSchema


def test_init(fake_api_call: ApiCall) -> None:
    """Test that the StopwordsSet object is initialized correctly."""
    stopword_set = StopwordsSet(fake_api_call, "company_stopwords")

    assert stopword_set.stopwords_set_id == "company_stopwords"
    assert_match_object(stopword_set.api_call, fake_api_call)
    assert_object_lists_match(
        stopword_set.api_call.node_manager.nodes,
        fake_api_call.node_manager.nodes,
    )
    assert_match_object(
        stopword_set.api_call.config.nearest_node,
        fake_api_call.config.nearest_node,
    )
    assert stopword_set._endpoint_path == "/stopwords/company_stopwords"  # noqa: WPS437


def test_retrieve(fake_stopwords_set: StopwordsSet) -> None:
    """Test that the StopwordsSet object can retrieve an stopword_set."""
    json_response: StopwordSchema = {
        "id": "company_stopwords",
        "stopwords": ["a", "an", "the"],
    }

    with requests_mock.Mocker() as mock:
        mock.get(
            "/stopwords/company_stopwords",
            json=json_response,
        )

        response = fake_stopwords_set.retrieve()

        assert len(mock.request_history) == 1
        assert mock.request_history[0].method == "GET"
        assert (
            mock.request_history[0].url
            == "http://nearest:8108/stopwords/company_stopwords"
        )
        assert response == json_response


def test_delete(fake_stopwords_set: StopwordsSet) -> None:
    """Test that the StopwordsSet object can delete an stopword_set."""
    json_response: StopwordDeleteSchema = {
        "id": "company_stopwords",
    }
    with requests_mock.Mocker() as mock:
        mock.delete(
            "/stopwords/company_stopwords",
            json=json_response,
        )

        response = fake_stopwords_set.delete()

        assert len(mock.request_history) == 1
        assert mock.request_history[0].method == "DELETE"
        assert (
            mock.request_history[0].url
            == "http://nearest:8108/stopwords/company_stopwords"
        )
        assert response == json_response


def test_actual_retrieve(
    actual_stopwords: Stopwords,
    delete_all_stopwords: None,
    delete_all: None,
    create_stopword: None,
) -> None:
    """Test that the StopwordsSet object can retrieve an stopword_set from Typesense Server."""
    response = actual_stopwords["company_stopwords"].retrieve()

    assert response == {
        "stopwords": {
            "id": "company_stopwords",
            "stopwords": ["and", "is", "the"],
        },
    }


def test_actual_delete(
    actual_stopwords: Stopwords,
    create_stopword: None,
) -> None:
    """Test that the StopwordsSet object can delete an stopword_set from Typesense Server."""
    response = actual_stopwords["company_stopwords"].delete()

    assert response == {"id": "company_stopwords"}
