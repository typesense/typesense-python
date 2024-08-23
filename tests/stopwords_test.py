"""Tests for the Stopwords class."""

from __future__ import annotations

import requests_mock

from tests.utils.object_assertions import (
    assert_match_object,
    assert_object_lists_match,
    assert_to_contain_object,
)
from typesense.api_call import ApiCall
from typesense.stopwords import Stopwords
from typesense.types.stopword import StopwordSchema, StopwordsRetrieveSchema


def test_init(fake_api_call: ApiCall) -> None:
    """Test that the Stopwords object is initialized correctly."""
    stopwords = Stopwords(fake_api_call)

    assert_match_object(stopwords.api_call, fake_api_call)
    assert_object_lists_match(stopwords.api_call.nodes, fake_api_call.nodes)
    assert_match_object(
        stopwords.api_call.config.nearest_node,
        fake_api_call.config.nearest_node,
    )

    assert not stopwords.stopwords_sets


def test_get_missing_stopword(fake_stopwords: Stopwords) -> None:
    """Test that the Stopwords object can get a missing stopword."""
    stopword = fake_stopwords["company_stopwords"]

    assert stopword.stopwords_set_id == "company_stopwords"
    assert_match_object(stopword.api_call, fake_stopwords.api_call)
    assert_object_lists_match(stopword.api_call.nodes, fake_stopwords.api_call.nodes)
    assert_match_object(
        stopword.api_call.config.nearest_node,
        fake_stopwords.api_call.config.nearest_node,
    )
    assert stopword._endpoint_path == "/stopwords/company_stopwords"  # noqa: WPS437


def test_get_existing_stopword(fake_stopwords: Stopwords) -> None:
    """Test that the Stopwords object can get an existing stopword."""
    stopword = fake_stopwords["company_stopwords"]
    fetched_stopword = fake_stopwords["company_stopwords"]

    assert len(fake_stopwords.stopwords_sets) == 1

    assert stopword is fetched_stopword


def test_retrieve(fake_stopwords: Stopwords) -> None:
    """Test that the Stopwords object can retrieve stopwords."""
    json_response: StopwordsRetrieveSchema = {
        "stopwords": [
            {
                "id": "company_stopwords",
                "locale": "",
                "stopwords": ["and", "is", "the"],
            },
        ],
    }

    with requests_mock.Mocker() as mock:
        mock.get(
            "http://nearest:8108/stopwords",
            json=json_response,
        )

        response = fake_stopwords.retrieve()

        assert len(response) == 1
        assert response["stopwords"][0] == json_response["stopwords"][0]
        assert response == json_response


def test_create(fake_stopwords: Stopwords) -> None:
    """Test that the Stopwords object can create a stopword."""
    json_response: StopwordSchema = {
        "id": "company_stopwords",
        "locale": "",
        "stopwords": ["and", "is", "the"],
    }

    with requests_mock.Mocker() as mock:
        mock.put(
            "http://nearest:8108/stopwords/company_stopwords",
            json=json_response,
        )

        fake_stopwords.upsert(
            "company_stopwords",
            {"stopwords": ["and", "is", "the"]},
        )

        assert mock.call_count == 1
        assert mock.called is True
        assert mock.last_request.method == "PUT"
        assert (
            mock.last_request.url == "http://nearest:8108/stopwords/company_stopwords"
        )
        assert mock.last_request.json() == {"stopwords": ["and", "is", "the"]}


def test_actual_create(actual_stopwords: Stopwords, delete_all_stopwords: None) -> None:
    """Test that the Stopwords object can create an stopword on Typesense Server."""
    response = actual_stopwords.upsert(
        "company_stopwords",
        {"stopwords": ["and", "is", "the"]},
    )

    assert response == {
        "id": "company_stopwords",
        "stopwords": ["and", "is", "the"],
    }


def test_actual_update(
    actual_stopwords: Stopwords,
    delete_all_stopwords: None,
) -> None:
    """Test that the Stopwords object can update an stopword on Typesense Server."""
    create_response = actual_stopwords.upsert(
        "company_stopwords",
        {"stopwords": ["and", "is", "the"]},
    )

    assert create_response == {
        "id": "company_stopwords",
        "stopwords": ["and", "is", "the"],
    }

    update_response = actual_stopwords.upsert(
        "company_stopwords",
        {"stopwords": ["and", "is", "other"]},
    )

    assert update_response == {
        "id": "company_stopwords",
        "stopwords": ["and", "is", "other"],
    }


def test_actual_retrieve(
    delete_all_stopwords: None,
    create_stopword: None,
    actual_stopwords: Stopwords,
) -> None:
    """Test that the Stopwords object can retrieve an stopword from Typesense Server."""
    response = actual_stopwords.retrieve()

    assert len(response["stopwords"]) == 1
    assert_to_contain_object(
        response["stopwords"][0],
        {
            "id": "company_stopwords",
            "stopwords": ["and", "is", "the"],
        },
    )
