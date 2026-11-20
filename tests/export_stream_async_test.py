"""Tests for streaming document exports with the async client."""

import asyncio
import gzip
import json
import sys

import httpx
import pytest
import respx

from tests.utils.backends import AsyncHandler, Backend, RequestType, load_backend
from tests.utils.streaming import (
    COLLECTION_PATH,
    COLLECTION_URL,
    EXPORT_PATH,
    EXPORT_URL,
)
from typesense.async_.api_call import AsyncApiCall
from typesense.async_.documents import AsyncDocuments
from typesense.async_.stream import AsyncExportStream
from typesense.configuration import Configuration
from typesense.exceptions import (
    ObjectNotFound,
    RequestMalformed,
    TypesenseClientError,
)
from typesense.http_backend import ResponseType
from typesense.types.document import DocumentSchema

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

TResult = typing.TypeVar("TResult")

BODY: typing.Final = b'{"id":"1"}\n{"id":"2"}\n{"id":"3"}'
LINES: typing.Final = ['{"id":"1"}', '{"id":"2"}', '{"id":"3"}']
WAIT_SECONDS: typing.Final = 1
SETTLE_SECONDS: typing.Final = 0.02


@pytest.fixture(name="backend", params=["httpx", "httpx2"])
def backend_fixture(request: pytest.FixtureRequest) -> Backend:
    """Return each HTTP backend that is installed."""
    name = request.param
    assert isinstance(name, str)
    return load_backend(name)


def make_api_call(
    backend: Backend,
    config: Configuration,
    handler: AsyncHandler,
) -> AsyncApiCall:
    """Return an API call that sends requests through a mock transport."""
    return AsyncApiCall(config, backend.async_client(handler))


def make_documents(
    backend: Backend,
    config: Configuration,
    handler: AsyncHandler,
) -> AsyncDocuments[DocumentSchema]:
    """Return documents sent through a mock transport of ``backend``."""
    return AsyncDocuments[DocumentSchema](
        make_api_call(backend, config, handler), "books"
    )


async def chunked(
    *chunks: bytes,
    error: typing.Optional[Exception] = None,
) -> typing.AsyncIterator[bytes]:
    """Yield ``chunks``, then raise ``error`` if there is one."""
    for chunk in chunks:
        yield chunk
    if error is not None:
        raise error


def respond_with(backend: Backend, *chunks: bytes) -> AsyncHandler:
    """Return a handler that sends ``chunks`` as a streamed export."""

    async def handler(request: RequestType) -> ResponseType:
        return backend.Response(200, content=chunked(*chunks))

    return handler


def fail_with(backend: Backend, error: Exception, *chunks: bytes) -> AsyncHandler:
    """Return a handler that sends ``chunks``, then fails while streaming."""

    async def handler(request: RequestType) -> ResponseType:
        return backend.Response(200, content=chunked(*chunks, error=error))

    return handler


async def read_lines(
    documents: AsyncDocuments[DocumentSchema],
    *,
    compress: bool = False,
) -> typing.List[str]:
    """Open an export and return all of its lines."""
    async with await documents.export_stream(compress=compress) as stream:
        return [line async for line in stream]


async def assert_waiting(task: "asyncio.Future[TResult]") -> None:
    """Assert that ``task`` has not finished after giving it time to run."""
    await asyncio.sleep(SETTLE_SECONDS)
    assert not task.done()


def limited_documents(
    config: Configuration,
    max_connections: typing.Optional[int],
    max_concurrent_requests: typing.Optional[int],
) -> AsyncDocuments[DocumentSchema]:
    """Return documents using the client's own connection pool."""
    config.max_connections = max_connections
    config.max_concurrent_requests = max_concurrent_requests
    return AsyncDocuments[DocumentSchema](AsyncApiCall(config), "books")


def export_response(request: httpx.Request) -> httpx.Response:
    """Return a complete export, as a fresh response for every request."""
    return httpx.Response(200, content=BODY)


def mock_export() -> respx.Route:
    """Mock the export endpoint with a complete export."""
    return respx.get(EXPORT_URL).mock(side_effect=export_response)


async def open_export(documents: AsyncDocuments[DocumentSchema]) -> AsyncExportStream:
    """Open an export, failing the test if it has to wait."""
    return await asyncio.wait_for(documents.export_stream(), WAIT_SECONDS)


async def test_yields_lines_without_their_line_feed(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that the lines are complete, including the unterminated last one."""
    documents = make_documents(backend, fake_config, respond_with(backend, BODY))

    assert await read_lines(documents) == LINES


async def test_sends_the_export_parameters(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that the request goes to the export endpoint with its parameters."""
    requests: typing.List[RequestType] = []

    async def handler(request: RequestType) -> ResponseType:
        requests.append(request)
        return backend.Response(200, content=BODY)

    documents = make_documents(backend, fake_config, handler)

    async with await documents.export_stream(
        {"filter_by": "year:>2000", "batch_size": 500},
    ):
        pass

    assert requests[0].method == "GET"
    assert requests[0].url.path == EXPORT_PATH
    assert requests[0].url.params["filter_by"] == "year:>2000"
    assert requests[0].url.params["batch_size"] == "500"


@pytest.mark.parametrize("ending", ["", "\n"])
@pytest.mark.parametrize("text", ["a b", "a b", "a\u0085b", "é€😀"])
async def test_a_body_split_anywhere_gives_the_same_lines(
    backend: Backend,
    fake_config: Configuration,
    text: str,
    ending: str,
) -> None:
    """Test Unicode separators and characters split across chunks."""
    expected = [
        json.dumps({"id": "1", "title": text}, ensure_ascii=False),
        '{"id":"2"}',
    ]
    body = ("\n".join(expected) + ending).encode()

    for offset in range(len(body) + 1):
        handler = respond_with(backend, body[:offset], body[offset:])
        documents = make_documents(backend, fake_config, handler)
        assert await read_lines(documents) == expected


async def test_lines_are_left_as_they_arrived(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that blank lines and carriage returns are kept."""
    body = b'a\n\n{"id":"1"}\r\nb\rc'
    documents = make_documents(backend, fake_config, respond_with(backend, body))

    lines = await read_lines(documents)

    assert lines == ["a", "", '{"id":"1"}\r', "b\rc"]
    assert json.loads(lines[2]) == {"id": "1"}


async def test_invalid_utf8_raises_after_the_lines_before_it(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that a line that cannot be decoded fails the export."""
    body = b'{"id":"1"}\n\xff\n{"id":"3"}\n{"id":"4"}'
    documents = make_documents(backend, fake_config, respond_with(backend, body))

    async with await documents.export_stream() as stream:
        assert await stream.__anext__() == '{"id":"1"}'
        with pytest.raises(UnicodeDecodeError):
            await stream.__anext__()
        with pytest.raises(TypesenseClientError, match="failed"):
            await stream.__anext__()


async def test_aiter_bytes_yields_the_body(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that the bytes are the body, unchanged."""
    handler = respond_with(backend, BODY[:7], BODY[7:])
    documents = make_documents(backend, fake_config, handler)

    async with await documents.export_stream() as stream:
        chunks = [chunk async for chunk in stream.aiter_bytes()]

    assert b"".join(chunks) == BODY


async def test_aiter_bytes_accepts_a_chunk_size(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that chunks are cut to the requested size."""
    documents = make_documents(backend, fake_config, respond_with(backend, b"abcde"))

    async with await documents.export_stream() as stream:
        chunks = [chunk async for chunk in stream.aiter_bytes(chunk_size=2)]

    assert chunks == [b"ab", b"cd", b"e"]


async def test_compressed_responses_are_decoded(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that gzip gives the same lines and bytes as an uncompressed export."""
    compressed = gzip.compress(BODY)

    async def handler(request: RequestType) -> ResponseType:
        return backend.Response(
            200,
            headers={"Content-Encoding": "gzip"},
            content=chunked(compressed[:9], compressed[9:]),
        )

    documents = make_documents(backend, fake_config, handler)

    assert await read_lines(documents, compress=True) == LINES
    async with await documents.export_stream(compress=True) as stream:
        assert b"".join([c async for c in stream.aiter_bytes()]) == BODY


async def test_requests_an_uncompressed_export_by_default(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test the ``Accept-Encoding`` sent with and without ``compress``."""
    requests: typing.List[RequestType] = []

    async def handler(request: RequestType) -> ResponseType:
        requests.append(request)
        return backend.Response(200, content=BODY)

    documents = make_documents(backend, fake_config, handler)

    await read_lines(documents)
    await read_lines(documents, compress=True)

    assert requests[0].headers["Accept-Encoding"] == "identity"
    assert "gzip" in requests[1].headers["Accept-Encoding"]


async def test_an_accept_encoding_in_additional_headers_is_kept(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that a configured header wins, whatever its case."""
    requests: typing.List[RequestType] = []

    async def handler(request: RequestType) -> ResponseType:
        requests.append(request)
        return backend.Response(200, content=BODY)

    fake_config.additional_headers = {"accept-encoding": "gzip"}
    documents = make_documents(backend, fake_config, handler)

    await read_lines(documents)

    assert requests[0].headers.get_list("Accept-Encoding") == ["gzip"]


async def test_uses_the_stream_read_timeout(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that reads wait for ``stream_read_timeout_seconds``."""
    requests: typing.List[RequestType] = []

    async def handler(request: RequestType) -> ResponseType:
        requests.append(request)
        return backend.Response(200, content=BODY)

    fake_config.stream_read_timeout_seconds = 12.5
    documents = make_documents(backend, fake_config, handler)

    await read_lines(documents)

    assert requests[0].extensions["timeout"]["read"] == 12.5


@pytest.mark.parametrize(
    "received",
    [b'{"id":"1"}\n{"id', b'{"id":"1"}\n'],
    ids=["mid-line", "line-boundary"],
)
async def test_truncated_body_raises_without_a_partial_line(
    backend: Backend,
    fake_config: Configuration,
    received: bytes,
) -> None:
    """Test that a cut-off export raises the backend's error."""
    error = backend.RemoteProtocolError("peer closed connection")
    handler = fail_with(backend, error, received)
    documents = make_documents(backend, fake_config, handler)
    lines: typing.List[str] = []

    async with await documents.export_stream() as stream:
        with pytest.raises(backend.RemoteProtocolError):
            async for line in stream:
                lines.append(line)

    assert lines == ['{"id":"1"}']


async def test_truncated_body_raises_from_aiter_bytes(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that the bytes view reports a cut-off export too."""
    error = backend.RemoteProtocolError("peer closed connection")
    documents = make_documents(backend, fake_config, fail_with(backend, error, b"a"))

    async with await documents.export_stream() as stream:
        with pytest.raises(backend.RemoteProtocolError):
            async for _ in stream.aiter_bytes():
                pass


async def test_reading_after_a_failure_does_not_look_complete(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that lines and bytes keep raising once a read has failed."""
    error = backend.ReadError("connection reset")
    handler = fail_with(backend, error, b"a\n")
    documents = make_documents(backend, fake_config, handler)

    async with await documents.export_stream() as stream:
        assert await stream.__anext__() == "a"
        with pytest.raises(backend.ReadError):
            await stream.__anext__()
        with pytest.raises(TypesenseClientError, match="Start a new export"):
            await stream.__anext__()

    async with await documents.export_stream() as stream:
        chunks = stream.aiter_bytes()
        assert await chunks.__anext__() == b"a\n"
        with pytest.raises(backend.ReadError):
            await chunks.__anext__()
        with pytest.raises(TypesenseClientError, match="Start a new export"):
            await chunks.__anext__()


async def test_reading_after_a_cancelled_read_does_not_look_complete(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that a read that timed out in the caller is not taken for the end."""
    never = asyncio.Event()

    async def body() -> typing.AsyncIterator[bytes]:
        yield b"a\n"
        await never.wait()

    async def handler(request: RequestType) -> ResponseType:
        return backend.Response(200, content=body())

    documents = make_documents(backend, fake_config, handler)

    async with await documents.export_stream() as stream:
        assert await stream.__anext__() == "a"
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(stream.__anext__(), SETTLE_SECONDS)
        with pytest.raises(TypesenseClientError, match="Start a new export"):
            await stream.__anext__()


async def test_iteration_can_stop_and_carry_on(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that leaving a loop keeps the connection and the position."""
    handler = respond_with(backend, b"a\nb\n", b"c\n")
    documents = make_documents(backend, fake_config, handler)

    async with await documents.export_stream() as stream:
        async for line in stream:
            assert line == "a"
            break
        assert not stream.response.is_closed
        assert [line async for line in stream] == ["b", "c"]


async def test_closing_early_closes_the_response_without_draining(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that the rest of the body is not read."""
    sent: typing.List[int] = []

    async def body() -> typing.AsyncIterator[bytes]:
        for index in range(1000):
            sent.append(index)
            yield b"a\n"

    async def handler(request: RequestType) -> ResponseType:
        return backend.Response(200, content=body())

    documents = make_documents(backend, fake_config, handler)

    async with await documents.export_stream() as stream:
        await stream.__anext__()

    assert stream.response.is_closed
    assert len(sent) == 1


async def test_a_request_inside_the_loop_does_not_wait_for_the_export(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that a reading export holds no concurrency slot."""

    async def handler(request: RequestType) -> ResponseType:
        if request.url.path == EXPORT_PATH:
            return backend.Response(200, content=chunked(BODY))
        return backend.Response(200, json={"name": "books"})

    fake_config.max_concurrent_requests = 1
    api_call = make_api_call(backend, fake_config, handler)
    documents = AsyncDocuments[DocumentSchema](api_call, "books")

    async with await documents.export_stream() as stream:
        async for _ in stream:
            collection = await asyncio.wait_for(
                api_call.get("/collections/books", dict),
                WAIT_SECONDS,
            )
            assert collection == {"name": "books"}


async def test_opening_an_export_takes_a_concurrency_slot(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that a request waits while an export is waiting for its headers."""
    export_started = asyncio.Event()
    send_headers = asyncio.Event()

    async def handler(request: RequestType) -> ResponseType:
        if request.url.path == EXPORT_PATH:
            export_started.set()
            await send_headers.wait()
            return backend.Response(200, content=BODY)
        return backend.Response(200, json={})

    fake_config.max_concurrent_requests = 1
    api_call = make_api_call(backend, fake_config, handler)
    documents = AsyncDocuments[DocumentSchema](api_call, "books")

    opening = asyncio.ensure_future(documents.export_stream())
    await asyncio.wait_for(export_started.wait(), WAIT_SECONDS)
    request = asyncio.ensure_future(api_call.get("/collections/books", dict))
    await assert_waiting(request)

    send_headers.set()
    stream = await asyncio.wait_for(opening, WAIT_SECONDS)
    await asyncio.wait_for(request, WAIT_SECONDS)
    await stream.aclose()


async def test_only_one_view_of_the_body_can_be_read(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that asking for a second view raises at the call."""
    documents = make_documents(backend, fake_config, respond_with(backend, BODY))

    async with await documents.export_stream() as stream:
        await stream.__anext__()
        with pytest.raises(TypesenseClientError, match="already being read"):
            stream.aiter_bytes()

    async with await documents.export_stream() as stream:
        stream.aiter_bytes()
        with pytest.raises(TypesenseClientError, match="already being read"):
            stream.__aiter__()
        with pytest.raises(TypesenseClientError, match="already being read"):
            stream.aiter_bytes()


async def test_error_responses_raise_when_opening(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that the error body is read and the request is not retried."""
    requests: typing.List[RequestType] = []

    async def handler(request: RequestType) -> ResponseType:
        requests.append(request)
        return backend.Response(400, json={"message": "Bad filter"})

    documents = make_documents(backend, fake_config, handler)

    with pytest.raises(RequestMalformed, match="Bad filter"):
        await documents.export_stream({"filter_by": "nope"})

    assert len(requests) == 1


async def test_fails_over_before_the_body_starts(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that a 5xx is retried on the next node, which is marked healthy."""
    hosts: typing.List[str] = []

    async def handler(request: RequestType) -> ResponseType:
        hosts.append(request.url.host)
        if request.url.host == "nearest":
            return backend.Response(503, text="Down")
        return backend.Response(200, content=BODY)

    documents = make_documents(backend, fake_config, handler)
    node = documents.api_call.node_manager.nodes[0]
    node.healthy = False
    node.last_access_ts = 0

    assert await read_lines(documents) == LINES

    assert hosts == ["nearest", "node0"]
    assert fake_config.nearest_node is not None
    assert fake_config.nearest_node.healthy is False
    assert node.healthy is True


async def test_does_not_retry_once_the_body_has_started(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that an error after the first chunk reaches the caller."""
    requests: typing.List[RequestType] = []

    async def handler(request: RequestType) -> ResponseType:
        requests.append(request)
        error = backend.ReadError("connection reset")
        return backend.Response(200, content=chunked(b"a\n", error=error))

    documents = make_documents(backend, fake_config, handler)

    async with await documents.export_stream() as stream:
        assert await stream.__anext__() == "a"
        with pytest.raises(backend.ReadError):
            await stream.__anext__()

    assert len(requests) == 1


async def test_reading_after_close_raises(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that a closed export cannot be mistaken for a finished one."""
    documents = make_documents(backend, fake_config, respond_with(backend, BODY))

    async with await documents.export_stream() as stream:
        await stream.__anext__()
    with pytest.raises(TypesenseClientError, match="closed"):
        await stream.__anext__()
    with pytest.raises(TypesenseClientError, match="closed"):
        stream.__aiter__()
    with pytest.raises(TypesenseClientError, match="closed"):
        stream.aiter_bytes()

    async with await documents.export_stream() as stream:
        chunks = stream.aiter_bytes()
    with pytest.raises(TypesenseClientError, match="closed"):
        await chunks.__anext__()


async def test_closing_while_another_task_reads(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that closing does not raise and the reader does not see a clean end."""
    end_body = asyncio.Event()

    async def body() -> typing.AsyncIterator[bytes]:
        yield b"a\n"
        await end_body.wait()

    async def handler(request: RequestType) -> ResponseType:
        return backend.Response(200, content=body())

    documents = make_documents(backend, fake_config, handler)
    stream = await documents.export_stream()
    assert await stream.__anext__() == "a"
    reader = asyncio.ensure_future(stream.__anext__())
    await assert_waiting(reader)

    await asyncio.wait_for(stream.aclose(), WAIT_SECONDS)

    end_body.set()
    with pytest.raises(TypesenseClientError, match="closed"):
        await asyncio.wait_for(reader, WAIT_SECONDS)


async def test_a_read_broken_by_closing_reports_the_close(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that the error a close causes does not look like a network failure."""
    break_read = asyncio.Event()

    async def body() -> typing.AsyncIterator[bytes]:
        yield b"a"
        await break_read.wait()
        raise backend.ReadError("connection closed")

    async def handler(request: RequestType) -> ResponseType:
        return backend.Response(200, content=body())

    documents = make_documents(backend, fake_config, handler)
    stream = await documents.export_stream()
    chunks = stream.aiter_bytes()
    assert await chunks.__anext__() == b"a"
    reader = asyncio.ensure_future(chunks.__anext__())
    await assert_waiting(reader)

    await asyncio.wait_for(stream.aclose(), WAIT_SECONDS)
    break_read.set()

    with pytest.raises(TypesenseClientError, match="closed"):
        await asyncio.wait_for(reader, WAIT_SECONDS)
    with pytest.raises(TypesenseClientError, match="closed"):
        await chunks.__anext__()


async def test_a_read_cancelled_after_close_stays_cancelled(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that cancelling a read is not turned into an error, even after a close."""
    end_body = asyncio.Event()

    async def body() -> typing.AsyncIterator[bytes]:
        yield b"a"
        await end_body.wait()

    async def handler(request: RequestType) -> ResponseType:
        return backend.Response(200, content=body())

    documents = make_documents(backend, fake_config, handler)
    stream = await documents.export_stream()
    chunks = stream.aiter_bytes()
    assert await chunks.__anext__() == b"a"
    reader = asyncio.ensure_future(chunks.__anext__())
    await assert_waiting(reader)
    await asyncio.wait_for(stream.aclose(), WAIT_SECONDS)

    reader.cancel()

    with pytest.raises(asyncio.CancelledError):
        await asyncio.wait_for(reader, WAIT_SECONDS)
    with pytest.raises(TypesenseClientError, match="closed"):
        await chunks.__anext__()


async def test_chunks_arriving_during_close_are_the_last_ones(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that the bytes view stops at the read that was already in progress."""
    send_more = asyncio.Event()

    async def body() -> typing.AsyncIterator[bytes]:
        yield b"a"
        await send_more.wait()
        yield b"b"
        yield b"c"

    async def handler(request: RequestType) -> ResponseType:
        return backend.Response(200, content=body())

    documents = make_documents(backend, fake_config, handler)
    stream = await documents.export_stream()
    chunks = stream.aiter_bytes()
    assert await chunks.__anext__() == b"a"
    reader = asyncio.ensure_future(chunks.__anext__())
    await assert_waiting(reader)

    await stream.aclose()
    send_more.set()

    assert await asyncio.wait_for(reader, WAIT_SECONDS) == b"b"
    with pytest.raises(TypesenseClientError, match="closed"):
        await chunks.__anext__()


@pytest.mark.parametrize(
    ("max_connections", "max_concurrent_requests", "places"),
    [(3, 2, 1), (5, 2, 3), (2, 2, 1), (1, 5, 1)],
)
async def test_open_exports_are_limited(
    fake_config: Configuration,
    max_connections: int,
    max_concurrent_requests: int,
    places: int,
) -> None:
    """Test the limit, including when the slots leave no room in the pool."""
    documents = limited_documents(fake_config, max_connections, max_concurrent_requests)

    with respx.mock:
        mock_export()
        streams = [await open_export(documents) for _ in range(places)]
        waiting = asyncio.ensure_future(documents.export_stream())
        await assert_waiting(waiting)

        await streams[0].aclose()
        streams[0] = await asyncio.wait_for(waiting, WAIT_SECONDS)

        for stream in streams:
            await stream.aclose()


async def test_closing_twice_gives_back_one_place(
    fake_config: Configuration,
) -> None:
    """Test that a second close cannot raise the limit."""
    documents = limited_documents(fake_config, 3, 2)

    with respx.mock:
        mock_export()
        stream = await open_export(documents)
        await stream.aclose()
        await stream.aclose()

        first = await open_export(documents)
        second = asyncio.ensure_future(documents.export_stream())
        await assert_waiting(second)
        await first.aclose()
        await (await asyncio.wait_for(second, WAIT_SECONDS)).aclose()


async def test_overlapping_closes_keep_the_place_until_the_response_closes(
    fake_config: Configuration,
) -> None:
    """Test that a second close cannot free the place while the first is closing."""
    finish_close = asyncio.Event()

    class SlowToClose(httpx.AsyncByteStream):
        """A body whose connection takes a while to close."""

        async def __aiter__(self) -> typing.AsyncIterator[bytes]:
            """Yield the whole body."""
            yield BODY

        async def aclose(self) -> None:
            """Wait until the test lets the close finish."""
            await asyncio.wait_for(finish_close.wait(), WAIT_SECONDS)

    documents = limited_documents(fake_config, 2, 1)

    with respx.mock:

        def respond(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, stream=SlowToClose())

        respx.get(EXPORT_URL).mock(side_effect=respond)
        stream = await open_export(documents)
        first_close = asyncio.ensure_future(stream.aclose())
        await assert_waiting(first_close)
        await asyncio.wait_for(stream.aclose(), WAIT_SECONDS)

        opening = asyncio.ensure_future(documents.export_stream())
        await assert_waiting(opening)

        finish_close.set()
        await asyncio.wait_for(first_close, WAIT_SECONDS)
        await (await asyncio.wait_for(opening, WAIT_SECONDS)).aclose()


async def test_exports_are_not_limited_without_a_concurrency_limit(
    fake_config: Configuration,
) -> None:
    """Test that the limit needs ``max_concurrent_requests``."""
    documents = limited_documents(fake_config, 1, None)

    with respx.mock:
        mock_export()
        streams = [await open_export(documents) for _ in range(3)]
        for stream in streams:
            await stream.aclose()


async def test_exports_are_not_limited_with_an_unlimited_pool(
    fake_config: Configuration,
) -> None:
    """Test that a pool without a size leaves nothing to reserve."""
    documents = limited_documents(fake_config, None, 2)

    with respx.mock:
        mock_export()
        streams = [await open_export(documents) for _ in range(3)]
        for stream in streams:
            await stream.aclose()


async def test_reading_to_the_end_gives_back_the_place(
    fake_config: Configuration,
) -> None:
    """Test that an export read to its end does not need closing."""
    documents = limited_documents(fake_config, 3, 2)

    with respx.mock:
        mock_export()
        lines_stream = await open_export(documents)
        lines = [line async for line in lines_stream]
        bytes_stream = await open_export(documents)
        body = b"".join([chunk async for chunk in bytes_stream.aiter_bytes()])
        await (await open_export(documents)).aclose()

    assert lines == LINES
    assert body == BODY


async def test_a_failed_read_gives_back_the_place(
    fake_config: Configuration,
) -> None:
    """Test that an export that failed does not need closing."""
    documents = limited_documents(fake_config, 3, 2)

    with respx.mock:

        def respond(request: httpx.Request) -> httpx.Response:
            error = httpx.ReadError("connection reset")
            return httpx.Response(200, content=chunked(b"a\n", error=error))

        route = respx.get(EXPORT_URL).mock(side_effect=respond)
        stream = await open_export(documents)
        with pytest.raises(httpx.ReadError):
            async for _ in stream:
                pass

        route.mock(side_effect=export_response)
        await (await open_export(documents)).aclose()


async def test_exports_are_not_limited_with_a_caller_supplied_client(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that the limit is skipped when the pool size is unknown."""
    fake_config.max_connections = 2
    fake_config.max_concurrent_requests = 1
    documents = make_documents(backend, fake_config, respond_with(backend, BODY))

    streams = [await open_export(documents) for _ in range(3)]

    for stream in streams:
        await stream.aclose()


async def test_a_failed_open_gives_back_its_slot_and_place(
    fake_config: Configuration,
) -> None:
    """Test that an error response leaves the next export free to open."""
    documents = limited_documents(fake_config, 2, 1)

    with respx.mock:
        route = respx.get(EXPORT_URL)
        route.mock(return_value=httpx.Response(404, json={"message": "Not found"}))
        with pytest.raises(ObjectNotFound, match="Not found"):
            await documents.export_stream()

        mock_export()
        await (await open_export(documents)).aclose()


async def test_cancelling_while_waiting_for_a_place(
    fake_config: Configuration,
) -> None:
    """Test that a cancelled export takes no place with it."""
    documents = limited_documents(fake_config, 3, 2)

    with respx.mock:
        mock_export()
        stream = await open_export(documents)
        waiting = asyncio.ensure_future(documents.export_stream())
        await assert_waiting(waiting)
        waiting.cancel()
        await asyncio.wait({waiting}, timeout=WAIT_SECONDS)
        await stream.aclose()

        first = await open_export(documents)
        second = asyncio.ensure_future(documents.export_stream())
        await assert_waiting(second)
        await first.aclose()
        await (await asyncio.wait_for(second, WAIT_SECONDS)).aclose()


async def test_an_export_waiting_for_a_place_holds_no_slot(
    fake_config: Configuration,
) -> None:
    """Test that requests keep running while an export waits its turn."""
    documents = limited_documents(fake_config, 2, 1)

    with respx.mock:
        mock_export()
        respx.get(COLLECTION_URL).mock(return_value=httpx.Response(200, json={}))
        stream = await open_export(documents)
        waiting = asyncio.ensure_future(documents.export_stream())
        await assert_waiting(waiting)

        await asyncio.wait_for(
            documents.api_call.get(COLLECTION_PATH, dict),
            WAIT_SECONDS,
        )

        await stream.aclose()
        await (await asyncio.wait_for(waiting, WAIT_SECONDS)).aclose()


async def test_cancelling_while_waiting_for_a_slot_gives_back_the_place(
    fake_config: Configuration,
) -> None:
    """Test that the place taken first is released."""
    finish_request = asyncio.Event()
    request_started = asyncio.Event()

    async def respond(request: httpx.Request) -> httpx.Response:
        request_started.set()
        await finish_request.wait()
        return httpx.Response(200, json={})

    documents = limited_documents(fake_config, 2, 1)

    with respx.mock:
        mock_export()
        respx.get(COLLECTION_URL).mock(side_effect=respond)
        request = asyncio.ensure_future(
            documents.api_call.get(COLLECTION_PATH, dict),
        )
        await asyncio.wait_for(request_started.wait(), WAIT_SECONDS)

        opening = asyncio.ensure_future(documents.export_stream())
        await assert_waiting(opening)
        opening.cancel()
        await asyncio.wait({opening}, timeout=WAIT_SECONDS)

        finish_request.set()
        await asyncio.wait_for(request, WAIT_SECONDS)
        await (await open_export(documents)).aclose()


async def test_cancelling_while_waiting_for_headers_gives_back_the_slot(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that a request can run after an export was cancelled while opening."""
    export_started = asyncio.Event()
    never = asyncio.Event()

    async def handler(request: RequestType) -> ResponseType:
        if request.url.path == EXPORT_PATH:
            export_started.set()
            await never.wait()
        return backend.Response(200, json={})

    fake_config.max_concurrent_requests = 1
    api_call = make_api_call(backend, fake_config, handler)
    documents = AsyncDocuments[DocumentSchema](api_call, "books")

    opening = asyncio.ensure_future(documents.export_stream())
    await asyncio.wait_for(export_started.wait(), WAIT_SECONDS)
    opening.cancel()
    await asyncio.wait({opening}, timeout=WAIT_SECONDS)

    await asyncio.wait_for(api_call.get("/collections/books", dict), WAIT_SECONDS)


async def test_export_stream_through_the_default_client(
    fake_config: Configuration,
) -> None:
    """Test the export without a client passed in."""
    documents = AsyncDocuments[DocumentSchema](AsyncApiCall(fake_config), "books")

    with respx.mock:
        mock_export()
        assert await read_lines(documents) == LINES
