"""Tests for the MultiSearch class."""

import pytest

from tests.fixtures.document_fixtures import Companies
from tests.utils.object_assertions import (
    assert_match_object,
    assert_object_lists_match,
    assert_to_contain_keys,
)
from typesense import exceptions
from typesense.api_call import ApiCall
from typesense.multi_search import MultiSearch
from typesense.types.multi_search import MultiSearchRequestSchema


def test_init(fake_api_call: ApiCall) -> None:
    """Test that the Document object is initialized correctly."""
    documents = MultiSearch(fake_api_call)

    assert_match_object(documents.api_call, fake_api_call)
    assert_object_lists_match(documents.api_call.nodes, fake_api_call.nodes)
    assert_match_object(
        documents.api_call.config.nearest_node,
        fake_api_call.config.nearest_node,
    )


def test_multi_search_single_search(
    actual_multi_search: MultiSearch,
    actual_api_call: ApiCall,
    delete_all: None,
    create_collection: None,
    create_document: None,
) -> None:
    """Test that the MultiSearch object can perform a single search."""
    request_params: MultiSearchRequestSchema = {
        "searches": [
            {"q": "com", "query_by": "company_name", "collection": "companies"},
        ],
    }
    response = actual_multi_search.perform(
        search_queries=request_params,
    )

    assert len(response.get("results")) == 1
    assert_to_contain_keys(
        response.get("results")[0],
        [
            "facet_counts",
            "found",
            "hits",
            "page",
            "out_of",
            "request_params",
            "search_time_ms",
            "search_cutoff",
        ],
    )

    assert_to_contain_keys(
        response.get("results")[0].get("hits")[0],
        ["document", "highlights", "highlight", "text_match", "text_match_info"],
    )


def test_multi_search_multiple_searches(
    actual_multi_search: MultiSearch,
    actual_api_call: ApiCall,
    delete_all: None,
    create_collection: None,
    create_document: None,
) -> None:
    """Test that the MultiSearch object can perform multiple searches."""
    request_params: MultiSearchRequestSchema = {
        "searches": [
            {"q": "com", "query_by": "company_name", "collection": "companies"},
            {"q": "company", "query_by": "company_name", "collection": "companies"},
        ],
    }

    response = actual_multi_search.perform(search_queries=request_params)

    assert len(response.get("results")) == len(request_params.get("searches"))
    for search_results in response.get("results"):
        assert_to_contain_keys(
            search_results,
            [
                "facet_counts",
                "found",
                "hits",
                "page",
                "out_of",
                "request_params",
                "search_time_ms",
                "search_cutoff",
            ],
        )

        assert_to_contain_keys(
            search_results.get("hits")[0],
            ["document", "highlights", "highlight", "text_match", "text_match_info"],
        )


def test_multi_search_array(
    actual_multi_search: MultiSearch,
    actual_api_call: ApiCall,
    delete_all: None,
    create_collection: None,
    create_document: None,
) -> None:
    """Test that the MultiSearch object can perform a search with an array query_by."""
    request_params: MultiSearchRequestSchema = {
        "searches": [
            {"q": "com", "query_by": ["company_name"], "collection": "companies"},
        ],
    }
    response = actual_multi_search.perform(search_queries=request_params)

    assert len(response.get("results")) == 1
    assert_to_contain_keys(
        response.get("results")[0],
        [
            "facet_counts",
            "found",
            "hits",
            "page",
            "out_of",
            "request_params",
            "search_time_ms",
            "search_cutoff",
        ],
    )

    assert_to_contain_keys(
        response.get("results")[0].get("hits")[0],
        ["document", "highlights", "highlight", "text_match", "text_match_info"],
    )


def test_search_invalid_parameters(
    actual_multi_search: MultiSearch,
    actual_api_call: ApiCall,
    delete_all: None,
    create_collection: None,
    create_document: None,
) -> None:
    """Test that the MultiSearch object raises an error when invalid parameters are passed."""
    with pytest.raises(exceptions.InvalidParameter):
        actual_multi_search.perform(
            {
                "searches": [
                    {
                        "q": "com",
                        "query_by": "company_name",
                        "invalid": [Companies(company_name="", id="", num_employees=0)],
                    },
                ],
            },
        )

    with pytest.raises(exceptions.InvalidParameter):
        actual_multi_search.perform(
            {
                "searches": [
                    {
                        "q": "com",
                        "query_by": "company_name",
                        "invalid": Companies(company_name="", id="", num_employees=0),
                    },
                ],
            },
        )
