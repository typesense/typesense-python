"""Tests for the Document class."""

from __future__ import annotations

import requests_mock

from tests.fixtures.document_fixtures import Companies
from tests.utils.object_assertions import (
    assert_match_object,
    assert_object_lists_match,
    assert_to_contain_object,
)
from typesense.api_call import ApiCall
from typesense.document import Document
from typesense.documents import Documents


def test_init(fake_api_call: ApiCall) -> None:
    """Test that the Document object is initialized correctly."""
    document = Document(fake_api_call, "companies", "0")

    assert document.document_id == "0"
    assert document.collection_name == "companies"
    assert_match_object(document.api_call, fake_api_call)
    assert_object_lists_match(document.api_call.nodes, fake_api_call.nodes)
    assert_match_object(
        document.api_call.config.nearest_node,
        fake_api_call.config.nearest_node,
    )
    assert (
        document._endpoint_path == "/collections/companies/documents/0"  # noqa: WPS437
    )


def test_retrieve(fake_document: Document) -> None:
    """Test that the Document object can retrieve an document."""
    json_response: Companies = {
        "company_name": "Company",
        "id": "0",
        "num_employees": 10,
    }

    with requests_mock.Mocker() as mock:
        mock.get(
            "http://nearest:8108/collections/companies/documents/0",
            json=json_response,
        )

        response = fake_document.retrieve()

        assert len(mock.request_history) == 1
        assert mock.request_history[0].method == "GET"
        assert (
            mock.request_history[0].url
            == "http://nearest:8108/collections/companies/documents/0"
        )
        assert response == json_response


def test_delete(fake_document: Document) -> None:
    """Test that the Document object can delete an document."""
    json_response: Companies = {
        "company_name": "Company",
        "id": "0",
        "num_employees": 10,
    }
    with requests_mock.Mocker() as mock:
        mock.delete(
            "http://nearest:8108/collections/companies/documents/0",
            json=json_response,
        )

        response = fake_document.delete()

        assert len(mock.request_history) == 1
        assert mock.request_history[0].method == "DELETE"
        assert (
            mock.request_history[0].url
            == "http://nearest:8108/collections/companies/documents/0"
        )
        assert response == json_response


def test_actual_update(
    actual_documents: Documents,
    delete_all: None,
    create_collection: None,
    create_document: None,
) -> None:
    """Test that the Document object can update an document on Typesense Server."""
    response = actual_documents["0"].update(
        {"company_name": "Company", "num_employees": 20},
        {
            "action": "update",
        },
    )

    assert_to_contain_object(
        response,
        {"id": "0", "company_name": "Company", "num_employees": 20},
    )


def test_actual_retrieve(
    actual_documents: Documents,
    delete_all: None,
    create_collection: None,
    create_document: None,
) -> None:
    """Test that the Document object can retrieve an document from Typesense Server."""
    response = actual_documents["0"].retrieve()

    assert_to_contain_object(
        response,
        {"id": "0", "company_name": "Company", "num_employees": 10},
    )


def test_actual_delete(
    actual_documents: Documents,
    delete_all: None,
    create_collection: None,
    create_document: None,
) -> None:
    """Test that the Document object can delete an document from Typesense Server."""
    response = actual_documents["0"].delete()

    assert response == {
        "id": "0",
        "company_name": "Company",
        "num_employees": 10,
    }
