"""Fixtures for streaming tests."""

import json
import os
import sys
from types import TracebackType

import pytest
import requests

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing


JSONPrimitive: typing.TypeAlias = typing.Union[str, int, float, bool, None]
JSONValue: typing.TypeAlias = typing.Union[
    JSONPrimitive, typing.Dict[str, "JSONValue"], typing.List["JSONValue"]
]
JSONDict: typing.TypeAlias = typing.Dict[str, JSONValue]


class FakeAsyncStreamResponse:
    """Minimal async streaming response for httpx.AsyncClient.stream()."""

    def __init__(
        self,
        *,
        lines: typing.Sequence[str],
        status_code: int = 200,
        headers: typing.Mapping[str, str] | None = None,
        text: str = "",
    ) -> None:
        self.status_code = status_code
        self._lines = list(lines)
        self.headers = dict(headers or {})
        self.text = text

    async def aiter_lines(self) -> typing.AsyncIterator[str]:
        for line in self._lines:
            yield line

    async def aread(self) -> bytes:
        return self.text.encode()

    def json(self) -> JSONDict:
        return typing.cast(JSONDict, json.loads(self.text))


class FakeAsyncStreamContext:
    """Async context manager that yields a fake streaming response."""

    def __init__(self, response: FakeAsyncStreamResponse) -> None:
        self._response = response

    async def __aenter__(self) -> FakeAsyncStreamResponse:
        return self._response

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        return None


class FakeStreamResponse:
    """Minimal streaming response for httpx.Client.stream()."""

    def __init__(
        self,
        *,
        lines: typing.Sequence[str],
        status_code: int = 200,
        headers: typing.Mapping[str, str] | None = None,
        text: str = "",
    ) -> None:
        self.status_code = status_code
        self._lines = list(lines)
        self.headers = dict(headers or {})
        self.text = text

    def iter_lines(self) -> typing.Iterator[str]:
        for line in self._lines:
            yield line

    def read(self) -> bytes:
        return self.text.encode()

    def json(self) -> JSONDict:
        return typing.cast(JSONDict, json.loads(self.text))


class FakeStreamContext:
    """Sync context manager that yields a fake streaming response."""

    def __init__(self, response: FakeStreamResponse) -> None:
        self._response = response

    def __enter__(self) -> FakeStreamResponse:
        return self._response

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        return None


@pytest.fixture(name="stream_response_async")
def stream_response_async_fixture() -> type[FakeAsyncStreamResponse]:
    return FakeAsyncStreamResponse


@pytest.fixture(name="stream_context_async")
def stream_context_async_fixture() -> type[FakeAsyncStreamContext]:
    return FakeAsyncStreamContext


@pytest.fixture(name="stream_response")
def stream_response_fixture() -> type[FakeStreamResponse]:
    return FakeStreamResponse


@pytest.fixture(name="stream_context")
def stream_context_fixture() -> type[FakeStreamContext]:
    return FakeStreamContext


@pytest.fixture(name="create_streaming_collection")
def create_streaming_collection_fixture(delete_all: None) -> str:
    """Create a collection for streaming tests with an auto-embedding field."""
    open_ai_key = os.environ.get("OPEN_AI_KEY")
    if not open_ai_key:
        pytest.skip("OPEN_AI_KEY is required for streaming integration tests.")
    url = "http://localhost:8108/collections"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}
    collection_data = {
        "name": "streaming_docs",
        "fields": [
            {
                "name": "title",
                "type": "string",
            },
            {
                "name": "embedding",
                "type": "float[]",
                "embed": {
                    "from": ["title"],
                    "model_config": {
                        "model_name": "openai/text-embedding-3-small",
                        "api_key": open_ai_key,
                    },
                },
            },
        ],
    }

    response = requests.post(url, headers=headers, json=collection_data, timeout=3)
    response.raise_for_status()
    return "streaming_docs"


@pytest.fixture(name="create_streaming_document")
def create_streaming_document_fixture(create_streaming_collection: str) -> str:
    """Create a document for streaming tests."""
    url = "http://localhost:8108/collections/streaming_docs/documents"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}
    document_data = {
        "id": "stream-1",
        "title": "Company profile",
    }

    response = requests.post(url, headers=headers, json=document_data, timeout=3)
    response.raise_for_status()
    return "stream-1"
