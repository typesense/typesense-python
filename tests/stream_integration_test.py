"""Tests for streamed conversational search against a Typesense server and OpenAI."""

import pytest

from typesense.async_.api_call import AsyncApiCall
from typesense.async_.documents import AsyncDocuments
from typesense.sync.api_call import ApiCall
from typesense.sync.documents import Documents
from typesense.sync.multi_search import MultiSearch


@pytest.mark.open_ai
def test_search_stream(
    delete_all: None,
    delete_all_conversations_models: None,
    create_collection: None,
    create_document: None,
    create_conversations_model: str,
    actual_api_call: ApiCall,
) -> None:
    """Test that the streamed pieces make up the answer in the search response."""
    documents = Documents(actual_api_call, "companies")

    with documents.search_stream(
        {
            "q": "company",
            "query_by": "company_name",
            "conversation_model_id": create_conversations_model,
        },
    ) as stream:
        messages = [chunk["message"] for chunk in stream]
        response = stream.get_final_response()

    assert messages
    assert response["found"] == 1
    assert "".join(messages) == response["conversation"]["answer"]


@pytest.mark.open_ai
async def test_search_stream_async(
    delete_all: None,
    delete_all_conversations_models: None,
    create_collection: None,
    create_document: None,
    create_conversations_model: str,
    actual_async_api_call: AsyncApiCall,
) -> None:
    """Test streaming with the async client."""
    documents = AsyncDocuments(actual_async_api_call, "companies")

    async with await documents.search_stream(
        {
            "q": "company",
            "query_by": "company_name",
            "conversation_model_id": create_conversations_model,
        },
    ) as stream:
        messages = [chunk["message"] async for chunk in stream]
        response = await stream.get_final_response()

    assert messages
    assert "".join(messages) == response["conversation"]["answer"]


@pytest.mark.open_ai
def test_multi_search_stream(
    delete_all: None,
    delete_all_conversations_models: None,
    create_collection: None,
    create_document: None,
    create_conversations_model: str,
    actual_api_call: ApiCall,
) -> None:
    """Test that a streamed multi-search answers once, at the top level."""
    with MultiSearch(actual_api_call).perform_stream(
        {"searches": [{"collection": "companies", "query_by": "company_name"}]},
        {"q": "company", "conversation_model_id": create_conversations_model},
    ) as stream:
        messages = [chunk["message"] for chunk in stream]
        response = stream.get_final_response()

    assert len(response["results"]) == 1
    assert "".join(messages) == response["conversation"]["answer"]
