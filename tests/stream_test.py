"""Tests for streamed conversational search with the sync client."""

import json
import sys

import httpx
import pytest
import respx

from tests.utils.streaming import (
    CHUNKS,
    FINAL_RESPONSE,
    SEARCH_URL,
    MULTI_SEARCH_URL,
    sse_body,
    sse_response,
)
from typesense.configuration import Configuration
from typesense.exceptions import RequestMalformed, TypesenseClientError
from typesense.sync.api_call import ApiCall
from typesense.sync.documents import Documents
from typesense.sync.multi_search import MultiSearch
from typesense.types.document import MessageChunk, StreamConfigBuilder

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

SEARCH_PARAMS: typing.Final = {
    "q": "who wrote it",
    "query_by": "title",
    "conversation_model_id": "conv-model",
}


@pytest.fixture(name="documents")
def documents_fixture(fake_api_call: ApiCall) -> Documents:
    """Return the documents of a collection, sent through the fake API call."""
    return Documents(fake_api_call, "books")


def test_search_stream_yields_chunks_then_final_response(
    documents: Documents,
) -> None:
    """Test that the stream yields each answer piece and keeps the search response."""
    with respx.mock:
        route = respx.get(SEARCH_URL).mock(return_value=sse_response())

        with documents.search_stream(SEARCH_PARAMS) as stream:
            chunks = list(stream)
            final_response = stream.get_final_response()

    assert chunks == CHUNKS
    assert final_response == FINAL_RESPONSE
    request = route.calls.last.request
    assert request.headers["Accept"] == "text/event-stream"
    assert request.url.params["conversation"] == "true"
    assert request.url.params["conversation_stream"] == "true"
    assert request.url.params["conversation_model_id"] == "conv-model"


def test_get_final_response_reads_the_whole_stream(documents: Documents) -> None:
    """Test that the search response can be read without iterating first."""
    with respx.mock:
        respx.get(SEARCH_URL).mock(return_value=sse_response())

        with documents.search_stream(SEARCH_PARAMS) as stream:
            assert stream.get_final_response() == FINAL_RESPONSE


def test_grouped_search_stream_keeps_final_response(documents: Documents) -> None:
    """A grouped response has grouped_hits in place of hits."""
    grouped_response = {
        **{key: value for key, value in FINAL_RESPONSE.items() if key != "hits"},
        "grouped_hits": [{"group_key": ["fiction"], "hits": FINAL_RESPONSE["hits"]}],
    }
    with respx.mock:
        respx.get(SEARCH_URL).mock(
            return_value=sse_response(final_response=grouped_response),
        )

        with documents.search_stream({**SEARCH_PARAMS, "group_by": "category"}) as stream:
            assert list(stream) == CHUNKS
            assert stream.get_final_response() == grouped_response


def test_search_stream_uses_the_stream_read_timeout(documents: Documents) -> None:
    """Test that streaming reads wait for ``stream_read_timeout_seconds``."""
    with respx.mock:
        route = respx.get(SEARCH_URL).mock(return_value=sse_response())

        with documents.search_stream(SEARCH_PARAMS) as stream:
            stream.get_final_response()

    timeout = route.calls.last.request.extensions["timeout"]
    assert timeout["read"] == 60.0
    assert timeout["connect"] == 0.001


def test_search_runs_stream_config_callbacks(documents: Documents) -> None:
    """Test that search runs the callbacks and returns the search response."""
    received: typing.List[object] = []

    with respx.mock:
        route = respx.get(SEARCH_URL).mock(return_value=sse_response())

        response = documents.search(
            {
                **SEARCH_PARAMS,
                "conversation": True,
                "conversation_stream": True,
                "stream_config": {
                    "on_chunk": received.append,
                    "on_complete": received.append,
                },
            },
        )

    assert response == FINAL_RESPONSE
    assert received == [*CHUNKS, FINAL_RESPONSE]
    assert "stream_config" not in route.calls.last.request.url.params


def test_search_accepts_a_stream_config_builder(documents: Documents) -> None:
    """Test that callbacks registered on a builder run."""
    stream_config: StreamConfigBuilder[typing.Any] = StreamConfigBuilder()
    messages: typing.List[str] = []

    @stream_config.on_chunk
    def on_chunk(chunk: MessageChunk) -> None:
        messages.append(chunk["message"])

    with respx.mock:
        respx.get(SEARCH_URL).mock(return_value=sse_response())

        documents.search(
            {
                **SEARCH_PARAMS,
                "conversation_stream": True,
                "stream_config": stream_config,
            },
        )

    assert "".join(messages) == "The Hobbit was written by Tolkien."


def test_search_without_stream_config_returns_final_response(
    documents: Documents,
) -> None:
    """Test that a streamed search with no callbacks returns the search response."""
    with respx.mock:
        respx.get(SEARCH_URL).mock(return_value=sse_response())

        response = documents.search({**SEARCH_PARAMS, "conversation_stream": True})

    assert response == FINAL_RESPONSE


def test_search_stream_fails_over_before_the_stream_starts(
    fake_api_call: ApiCall,
    documents: Documents,
) -> None:
    """Test that a 5xx is retried on the next node, which is marked healthy."""
    node0_search_url = SEARCH_URL.replace("nearest", "node0")
    with respx.mock:
        respx.get(SEARCH_URL).mock(return_value=httpx.Response(503, text="Down"))
        respx.get(node0_search_url).mock(return_value=sse_response())

        with documents.search_stream(SEARCH_PARAMS) as stream:
            final_response = stream.get_final_response()

        assert len(respx.calls) == 2

    assert final_response == FINAL_RESPONSE
    assert fake_api_call.config.nearest_node is not None
    assert fake_api_call.config.nearest_node.healthy is False
    assert fake_api_call.config.nodes[0].healthy is True


def test_errors_mid_stream_are_raised_without_retrying(documents: Documents) -> None:
    """Test that a read error after the answer started is raised, not retried."""
    errors: typing.List[BaseException] = []
    received: typing.List[object] = []

    def body() -> typing.Iterator[bytes]:
        yield sse_body(CHUNKS[:1])
        raise httpx.ReadError("connection reset")

    with respx.mock:
        respx.get(SEARCH_URL).mock(return_value=sse_response(body()))

        with pytest.raises(httpx.ReadError):
            documents.search(
                {
                    **SEARCH_PARAMS,
                    "conversation_stream": True,
                    "stream_config": {
                        "on_chunk": received.append,
                        "on_error": errors.append,
                    },
                },
            )

        assert len(respx.calls) == 1

    assert received == CHUNKS[:1]
    assert len(errors) == 1
    assert isinstance(errors[0], httpx.ReadError)


def test_stream_ending_without_search_response_raises(documents: Documents) -> None:
    """Test that an error appended after the answer started is raised."""
    body = sse_body(CHUNKS) + b'{"message": "Conversation history is full."}'
    with respx.mock:
        respx.get(SEARCH_URL).mock(return_value=sse_response(body))

        with documents.search_stream(SEARCH_PARAMS) as stream:
            with pytest.raises(TypesenseClientError, match="history is full"):
                stream.get_final_response()


def test_client_errors_are_raised_and_reported_once(documents: Documents) -> None:
    """Test that a 400 with a plain-text body raises without failing over."""
    errors: typing.List[BaseException] = []
    with respx.mock:
        respx.get(SEARCH_URL).mock(
            return_value=httpx.Response(400, text="Conversation model not found"),
        )

        with pytest.raises(RequestMalformed, match="Conversation model not found"):
            documents.search(
                {
                    **SEARCH_PARAMS,
                    "conversation_stream": True,
                    "stream_config": {"on_error": errors.append},
                },
            )

        assert len(respx.calls) == 1

    assert len(errors) == 1


def test_closing_early_releases_the_connection_and_slot(
    fake_config: Configuration,
) -> None:
    """Test that leaving the stream early closes the response and frees its slot."""
    fake_config.max_concurrent_requests = 1
    api_call = ApiCall(fake_config)
    documents = Documents(api_call, "books")

    with respx.mock:
        respx.get(SEARCH_URL).mock(return_value=sse_response())

        with documents.search_stream(SEARCH_PARAMS) as stream:
            assert next(iter(stream)) == CHUNKS[0]

        with documents.search_stream(SEARCH_PARAMS) as second_stream:
            assert second_stream.get_final_response() == FINAL_RESPONSE

    assert stream.response.is_closed
    with pytest.raises(TypesenseClientError, match="closed before"):
        stream.get_final_response()


def test_multi_search_stream_sends_conversation_params_in_query(
    fake_api_call: ApiCall,
) -> None:
    """Test that multi-search streams with the conversation in the query string."""
    multi_search_response = {"results": [FINAL_RESPONSE], "conversation": {}}
    with respx.mock:
        route = respx.post(MULTI_SEARCH_URL).mock(
            return_value=sse_response(final_response=multi_search_response),
        )

        with MultiSearch(fake_api_call).perform_stream(
            {"searches": [{"collection": "books", "query_by": "title"}]},
            {"q": "who wrote it", "conversation_model_id": "conv-model"},
        ) as stream:
            chunks = list(stream)
            final_response = stream.get_final_response()

    assert chunks == CHUNKS
    assert final_response == multi_search_response
    request = route.calls.last.request
    assert request.url.params["q"] == "who wrote it"
    assert request.url.params["conversation_stream"] == "true"
    assert json.loads(request.content)["searches"] == [
        {"collection": "books", "query_by": "title"},
    ]


def test_multi_search_stream_accepts_a_json_response(fake_api_call: ApiCall) -> None:
    """Test the plain JSON Typesense sends when every search fails."""
    multi_search_response = {"results": [{"code": 404, "error": "Not found."}]}
    with respx.mock:
        respx.post(MULTI_SEARCH_URL).mock(
            return_value=httpx.Response(200, json=multi_search_response),
        )

        response = MultiSearch(fake_api_call).perform(
            {"searches": [{"collection": "missing", "query_by": "title"}]},
            {"q": "who", "conversation_model_id": "m", "conversation_stream": True},
        )

    assert response == multi_search_response


def test_search_stream_with_httpx2_client(fake_config: Configuration) -> None:
    """Test streaming through a user-supplied httpx2 client."""
    httpx2 = pytest.importorskip("httpx2")

    def handler(request: typing.Any) -> typing.Any:
        return httpx2.Response(
            200,
            headers={"Content-Type": "text/event-stream"},
            content=sse_body(CHUNKS, FINAL_RESPONSE),
        )

    http_client = httpx2.Client(transport=httpx2.MockTransport(handler))
    documents = Documents(ApiCall(fake_config, http_client), "books")

    with documents.search_stream(SEARCH_PARAMS) as stream:
        assert list(stream) == CHUNKS
        assert stream.get_final_response() == FINAL_RESPONSE
