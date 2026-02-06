"""Sync streaming conversation search tests."""

import sys

import pytest

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

from tests.fixtures.streaming_fixtures import (
    FakeStreamContext,
    FakeStreamResponse,
    JSONValue,
)
from typesense.exceptions import ServerError
from typesense.sync.documents import Documents
from typesense.types.document import (
    DocumentSchema,
    MessageChunk,
    StreamConfig,
    StreamConfigBuilder,
)


def test_streaming_search_invokes_on_chunk(
    fake_documents: Documents[DocumentSchema],
    stream_response: type[FakeStreamResponse],
    stream_context: type[FakeStreamContext],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that streaming search invokes on_chunk for each message chunk."""
    chunks_received: typing.List[MessageChunk] = []

    def on_chunk(chunk: MessageChunk) -> None:
        chunks_received.append(chunk)

    stream_config: StreamConfig[DocumentSchema] = {"on_chunk": on_chunk}

    sse_lines = [
        'data: {"conversation_id":"123","message":"First chunk"}',
        'data: {"conversation_id":"123","message":"Second chunk"}',
        '{"found": 2, "hits": [], "page": 1, "search_time_ms": 10}',
    ]
    response = stream_response(lines=sse_lines)

    def fake_stream(
        method: str,
        url: str,
        params: typing.Mapping[str, str] | None = None,
        content: str | bytes | None = None,
        headers: typing.Mapping[str, str] | None = None,
        timeout: float | None = None,
    ) -> FakeStreamContext:
        return stream_context(response)

    monkeypatch.setattr(
        fake_documents.api_call._client,
        "stream",
        fake_stream,
    )

    result = fake_documents.search(
        {
            "q": "test query",
            "query_by": "title",
            "conversation_stream": True,
            "stream_config": stream_config,
        }
    )

    assert len(chunks_received) == 2
    assert chunks_received[0]["message"] == "First chunk"
    assert chunks_received[1]["message"] == "Second chunk"
    assert result["found"] == 2


def test_streaming_search_handles_plain_text_lines(
    fake_documents: Documents[DocumentSchema],
    stream_response: type[FakeStreamResponse],
    stream_context: type[FakeStreamContext],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Plain text lines should be treated as message chunks with unknown id."""
    chunks_received: typing.List[MessageChunk] = []

    def on_chunk(chunk: MessageChunk) -> None:
        chunks_received.append(chunk)

    sse_lines = [
        "Hello",
        '{"found": 1, "hits": [], "page": 1, "search_time_ms": 5}',
    ]
    response = stream_response(lines=sse_lines)

    def fake_stream(
        method: str,
        url: str,
        params: typing.Mapping[str, str] | None = None,
        content: str | bytes | None = None,
        headers: typing.Mapping[str, str] | None = None,
        timeout: float | None = None,
    ) -> FakeStreamContext:
        return stream_context(response)

    monkeypatch.setattr(
        fake_documents.api_call._client,
        "stream",
        fake_stream,
    )

    fake_documents.search(
        {
            "q": "test",
            "query_by": "title",
            "conversation_stream": True,
            "stream_config": {"on_chunk": on_chunk},
        }
    )

    assert len(chunks_received) == 1
    assert chunks_received[0]["conversation_id"] == "unknown"
    assert chunks_received[0]["message"] == "Hello"


def test_streaming_search_handles_missing_fields(
    fake_documents: Documents[DocumentSchema],
    stream_response: type[FakeStreamResponse],
    stream_context: type[FakeStreamContext],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """JSON lines without conversation_id/message should use defaults."""
    chunks_received: typing.List[MessageChunk] = []

    def on_chunk(chunk: MessageChunk) -> None:
        chunks_received.append(chunk)

    sse_lines = [
        'data: {"foo":"bar"}',
        '{"found": 1, "hits": [], "page": 1, "search_time_ms": 5}',
    ]
    response = stream_response(lines=sse_lines)

    def fake_stream(
        method: str,
        url: str,
        params: typing.Mapping[str, str] | None = None,
        content: str | bytes | None = None,
        headers: typing.Mapping[str, str] | None = None,
        timeout: float | None = None,
    ) -> FakeStreamContext:
        return stream_context(response)

    monkeypatch.setattr(
        fake_documents.api_call._client,
        "stream",
        fake_stream,
    )

    fake_documents.search(
        {
            "q": "test",
            "query_by": "title",
            "conversation_stream": True,
            "stream_config": {"on_chunk": on_chunk},
        }
    )

    assert len(chunks_received) == 1
    assert chunks_received[0]["conversation_id"] == "unknown"
    assert chunks_received[0]["message"] == ""


def test_streaming_search_skips_done_marker(
    fake_documents: Documents[DocumentSchema],
    stream_response: type[FakeStreamResponse],
    stream_context: type[FakeStreamContext],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """data: [DONE] lines should be ignored."""
    chunks_received: typing.List[MessageChunk] = []

    def on_chunk(chunk: MessageChunk) -> None:
        chunks_received.append(chunk)

    sse_lines = [
        'data: {"conversation_id":"123","message":"Chunk"}',
        "data: [DONE]",
        '{"found": 1, "hits": [], "page": 1, "search_time_ms": 1}',
    ]
    response = stream_response(lines=sse_lines)

    def fake_stream(
        method: str,
        url: str,
        params: typing.Mapping[str, str] | None = None,
        content: str | bytes | None = None,
        headers: typing.Mapping[str, str] | None = None,
        timeout: float | None = None,
    ) -> FakeStreamContext:
        return stream_context(response)

    monkeypatch.setattr(
        fake_documents.api_call._client,
        "stream",
        fake_stream,
    )

    fake_documents.search(
        {
            "q": "test",
            "query_by": "title",
            "conversation_stream": True,
            "stream_config": {"on_chunk": on_chunk},
        }
    )

    assert len(chunks_received) == 1


def test_streaming_search_handles_json_array_lines(
    fake_documents: Documents[DocumentSchema],
    stream_response: type[FakeStreamResponse],
    stream_context: type[FakeStreamContext],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """JSON arrays should be treated as plain text message chunks."""
    chunks_received: typing.List[MessageChunk] = []

    def on_chunk(chunk: MessageChunk) -> None:
        chunks_received.append(chunk)

    sse_lines = [
        'data: ["a", "b"]',
        '{"found": 1, "hits": [], "page": 1, "search_time_ms": 1}',
    ]
    response = stream_response(lines=sse_lines)

    def fake_stream(
        method: str,
        url: str,
        params: typing.Mapping[str, str] | None = None,
        content: str | bytes | None = None,
        headers: typing.Mapping[str, str] | None = None,
        timeout: float | None = None,
    ) -> FakeStreamContext:
        return stream_context(response)

    monkeypatch.setattr(
        fake_documents.api_call._client,
        "stream",
        fake_stream,
    )

    fake_documents.search(
        {
            "q": "test",
            "query_by": "title",
            "conversation_stream": True,
            "stream_config": {"on_chunk": on_chunk},
        }
    )

    assert len(chunks_received) == 1
    assert chunks_received[0]["message"] == '["a", "b"]'


def test_streaming_search_supports_builder(
    fake_documents: Documents[DocumentSchema],
    stream_response: type[FakeStreamResponse],
    stream_context: type[FakeStreamContext],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test StreamConfigBuilder for streaming callbacks."""
    complete_calls: typing.List[int] = []

    stream = StreamConfigBuilder()

    @stream.on_complete
    def on_complete(response: typing.Mapping[str, JSONValue]) -> None:
        found = response.get("found")
        if isinstance(found, int):
            complete_calls.append(found)

    sse_lines = [
        'data: {"conversation_id":"123","message":"Hello"}',
        '{"found": 1, "hits": [], "page": 1, "search_time_ms": 5}',
    ]
    response = stream_response(lines=sse_lines)

    def fake_stream(
        method: str,
        url: str,
        params: typing.Mapping[str, str] | None = None,
        content: str | bytes | None = None,
        headers: typing.Mapping[str, str] | None = None,
        timeout: float | None = None,
    ) -> FakeStreamContext:
        return stream_context(response)

    monkeypatch.setattr(
        fake_documents.api_call._client,
        "stream",
        fake_stream,
    )

    fake_documents.search(
        {
            "q": "test",
            "query_by": "title",
            "conversation_stream": True,
            "stream_config": stream,
        }
    )

    assert complete_calls == [1]


def test_stream_config_not_sent_to_api(
    fake_documents: Documents[DocumentSchema],
    stream_response: type[FakeStreamResponse],
    stream_context: type[FakeStreamContext],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that stream_config is removed from API params."""
    captured_params: typing.Dict[str, str] = {}

    sse_lines = [
        '{"found": 0, "hits": [], "page": 1, "search_time_ms": 1}',
    ]
    response = stream_response(lines=sse_lines)

    def fake_stream(
        method: str,
        url: str,
        params: typing.Mapping[str, str] | None = None,
        content: str | bytes | None = None,
        headers: typing.Mapping[str, str] | None = None,
        timeout: float | None = None,
    ) -> FakeStreamContext:
        if params:
            captured_params.update(params)
        return stream_context(response)

    monkeypatch.setattr(
        fake_documents.api_call._client,
        "stream",
        fake_stream,
    )

    stream_config: StreamConfig[DocumentSchema] = {"on_chunk": lambda _: None}
    fake_documents.search(
        {
            "q": "test",
            "query_by": "title",
            "conversation_stream": True,
            "stream_config": stream_config,
        }
    )

    assert "stream_config" not in captured_params
    assert captured_params.get("conversation_stream") == "true"


def test_streaming_search_invokes_on_error(
    fake_documents: Documents[DocumentSchema],
    stream_response: type[FakeStreamResponse],
    stream_context: type[FakeStreamContext],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that streaming search invokes on_error for request failures."""
    errors: typing.List[BaseException] = []

    def on_error(error: BaseException) -> None:
        errors.append(error)

    fake_documents.api_call.config.num_retries = 0

    response = stream_response(
        lines=[],
        status_code=500,
        headers={"Content-Type": "application/json"},
        text='{"message": "Server error"}',
    )

    def fake_stream(
        method: str,
        url: str,
        params: typing.Mapping[str, str] | None = None,
        content: str | bytes | None = None,
        headers: typing.Mapping[str, str] | None = None,
        timeout: float | None = None,
    ) -> FakeStreamContext:
        return stream_context(response)

    monkeypatch.setattr(
        fake_documents.api_call._client,
        "stream",
        fake_stream,
    )

    with pytest.raises(ServerError):
        fake_documents.search(
            {
                "q": "test",
                "query_by": "title",
                "conversation_stream": True,
                "stream_config": {"on_error": on_error},
            }
        )

    assert len(errors) == 1
    assert isinstance(errors[0], ServerError)
