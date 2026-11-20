"""Tests for streaming document exports with the sync client."""

import gzip
import json
import sys
import threading
from concurrent.futures import Future, wait

import httpx
import pytest
import respx

from tests.utils.backends import Backend, Handler, RequestType, load_backend
from tests.utils.streaming import (
    COLLECTION_PATH,
    COLLECTION_URL,
    EXPORT_PATH,
    EXPORT_URL,
)
from typesense.configuration import Configuration
from typesense.exceptions import (
    ObjectNotFound,
    RequestMalformed,
    TypesenseClientError,
)
from typesense.sync.api_call import ApiCall
from typesense.sync.documents import Documents
from typesense.http_backend import ResponseType
from typesense.types.document import DocumentSchema
from typesense.sync.stream import ExportStream

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

TResult = typing.TypeVar("TResult")

BODY: typing.Final = b'{"id":"1"}\n{"id":"2"}\n{"id":"3"}'
LINES: typing.Final = ['{"id":"1"}', '{"id":"2"}', '{"id":"3"}']
WAIT_SECONDS: typing.Final = 2
SETTLE_SECONDS: typing.Final = 0.05


class Background(typing.Generic[TResult]):
    """Runs a call in a daemon thread, so a call that hangs cannot hang the tests."""

    def __init__(self, function: typing.Callable[[], TResult]) -> None:
        """Start running ``function``."""
        self._outcome: "Future[TResult]" = Future()
        threading.Thread(target=self._run, args=(function,), daemon=True).start()

    def _run(self, function: typing.Callable[[], TResult]) -> None:
        """Keep the outcome of the call."""
        try:
            self._outcome.set_result(function())
        except BaseException as error:  # noqa: B902 (reported by ``result``)
            self._outcome.set_exception(error)

    def assert_waiting(self) -> None:
        """Assert that the call has not finished after giving it time to run."""
        assert not wait([self._outcome], SETTLE_SECONDS).done

    def result(self) -> TResult:
        """Return the call's result, failing the test if it does not finish."""
        return self._outcome.result(WAIT_SECONDS)


@pytest.fixture(name="backend", params=["httpx", "httpx2"])
def backend_fixture(request: pytest.FixtureRequest) -> Backend:
    """Return each HTTP backend that is installed."""
    name = request.param
    assert isinstance(name, str)
    return load_backend(name)


def make_api_call(
    backend: Backend,
    config: Configuration,
    handler: Handler,
) -> ApiCall:
    """Return an API call that sends requests through a mock transport."""
    return ApiCall(config, backend.client(handler))


def make_documents(
    backend: Backend,
    config: Configuration,
    handler: Handler,
) -> Documents[DocumentSchema]:
    """Return documents sent through a mock transport of ``backend``."""
    return Documents[DocumentSchema](make_api_call(backend, config, handler), "books")


def chunked(
    *chunks: bytes,
    error: typing.Optional[Exception] = None,
) -> typing.Iterator[bytes]:
    """Yield ``chunks``, then raise ``error`` if there is one."""
    yield from chunks
    if error is not None:
        raise error


def respond_with(backend: Backend, *chunks: bytes) -> Handler:
    """Return a handler that sends ``chunks`` as a streamed export."""

    def handler(request: RequestType) -> ResponseType:
        return backend.Response(200, content=chunked(*chunks))

    return handler


def fail_with(backend: Backend, error: Exception, *chunks: bytes) -> Handler:
    """Return a handler that sends ``chunks``, then fails while streaming."""

    def handler(request: RequestType) -> ResponseType:
        return backend.Response(200, content=chunked(*chunks, error=error))

    return handler


def read_lines(
    documents: Documents[DocumentSchema], *, compress: bool = False
) -> typing.List[str]:
    """Open an export and return all of its lines."""
    with documents.export_stream(compress=compress) as stream:
        return list(stream)


def limited_documents(
    config: Configuration,
    max_connections: typing.Optional[int],
    max_concurrent_requests: typing.Optional[int],
) -> Documents[DocumentSchema]:
    """Return documents using the client's own connection pool."""
    config.max_connections = max_connections
    config.max_concurrent_requests = max_concurrent_requests
    return Documents[DocumentSchema](ApiCall(config), "books")


def export_response(request: httpx.Request) -> httpx.Response:
    """Return a complete export, as a fresh response for every request."""
    return httpx.Response(200, content=BODY)


def mock_export() -> respx.Route:
    """Mock the export endpoint with a complete export."""
    return respx.get(EXPORT_URL).mock(side_effect=export_response)


def open_export(documents: Documents[DocumentSchema]) -> ExportStream:
    """Open an export, failing the test if it has to wait."""
    return Background(documents.export_stream).result()


def test_yields_lines_without_their_line_feed(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that the lines are complete, including the unterminated last one."""
    documents = make_documents(backend, fake_config, respond_with(backend, BODY))

    assert read_lines(documents) == LINES


def test_sends_the_export_parameters(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that the request goes to the export endpoint with its parameters."""
    requests: typing.List[RequestType] = []

    def handler(request: RequestType) -> ResponseType:
        requests.append(request)
        return backend.Response(200, content=BODY)

    documents = make_documents(backend, fake_config, handler)

    with documents.export_stream({"filter_by": "year:>2000", "batch_size": 500}):
        pass

    assert requests[0].method == "GET"
    assert requests[0].url.path == EXPORT_PATH
    assert requests[0].url.params["filter_by"] == "year:>2000"
    assert requests[0].url.params["batch_size"] == "500"


@pytest.mark.parametrize("ending", ["", "\n"])
@pytest.mark.parametrize("text", ["a b", "a b", "a\u0085b", "é€😀"])
def test_a_body_split_anywhere_gives_the_same_lines(
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
        assert read_lines(documents) == expected


def test_lines_are_left_as_they_arrived(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that blank lines and carriage returns are kept."""
    body = b'a\n\n{"id":"1"}\r\nb\rc'
    documents = make_documents(backend, fake_config, respond_with(backend, body))

    lines = read_lines(documents)

    assert lines == ["a", "", '{"id":"1"}\r', "b\rc"]
    assert json.loads(lines[2]) == {"id": "1"}


def test_invalid_utf8_raises_after_the_lines_before_it(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that a line that cannot be decoded fails the export."""
    body = b'{"id":"1"}\n\xff\n{"id":"3"}\n{"id":"4"}'
    documents = make_documents(backend, fake_config, respond_with(backend, body))

    with documents.export_stream() as stream:
        assert next(stream) == '{"id":"1"}'
        with pytest.raises(UnicodeDecodeError):
            next(stream)
        with pytest.raises(TypesenseClientError, match="failed"):
            next(stream)


def test_iter_bytes_yields_the_body(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that the bytes are the body, unchanged."""
    handler = respond_with(backend, BODY[:7], BODY[7:])
    documents = make_documents(backend, fake_config, handler)

    with documents.export_stream() as stream:
        assert b"".join(stream.iter_bytes()) == BODY


def test_iter_bytes_accepts_a_chunk_size(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that chunks are cut to the requested size."""
    documents = make_documents(backend, fake_config, respond_with(backend, b"abcde"))

    with documents.export_stream() as stream:
        assert list(stream.iter_bytes(chunk_size=2)) == [b"ab", b"cd", b"e"]


def test_compressed_responses_are_decoded(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that gzip gives the same lines and bytes as an uncompressed export."""
    compressed = gzip.compress(BODY)

    def handler(request: RequestType) -> ResponseType:
        return backend.Response(
            200,
            headers={"Content-Encoding": "gzip"},
            content=chunked(compressed[:9], compressed[9:]),
        )

    documents = make_documents(backend, fake_config, handler)

    assert read_lines(documents, compress=True) == LINES
    with documents.export_stream(compress=True) as stream:
        assert b"".join(stream.iter_bytes()) == BODY


def test_requests_an_uncompressed_export_by_default(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test the ``Accept-Encoding`` sent with and without ``compress``."""
    requests: typing.List[RequestType] = []

    def handler(request: RequestType) -> ResponseType:
        requests.append(request)
        return backend.Response(200, content=BODY)

    documents = make_documents(backend, fake_config, handler)

    read_lines(documents)
    read_lines(documents, compress=True)

    assert requests[0].headers["Accept-Encoding"] == "identity"
    assert "gzip" in requests[1].headers["Accept-Encoding"]


def test_an_accept_encoding_in_additional_headers_is_kept(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that a configured header wins, whatever its case."""
    requests: typing.List[RequestType] = []

    def handler(request: RequestType) -> ResponseType:
        requests.append(request)
        return backend.Response(200, content=BODY)

    fake_config.additional_headers = {"accept-encoding": "gzip"}
    documents = make_documents(backend, fake_config, handler)

    read_lines(documents)

    assert requests[0].headers.get_list("Accept-Encoding") == ["gzip"]


def test_uses_the_stream_read_timeout(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that reads wait for ``stream_read_timeout_seconds``."""
    requests: typing.List[RequestType] = []

    def handler(request: RequestType) -> ResponseType:
        requests.append(request)
        return backend.Response(200, content=BODY)

    fake_config.stream_read_timeout_seconds = 12.5
    documents = make_documents(backend, fake_config, handler)

    read_lines(documents)

    assert requests[0].extensions["timeout"]["read"] == 12.5


@pytest.mark.parametrize(
    "received",
    [b'{"id":"1"}\n{"id', b'{"id":"1"}\n'],
    ids=["mid-line", "line-boundary"],
)
def test_truncated_body_raises_without_a_partial_line(
    backend: Backend,
    fake_config: Configuration,
    received: bytes,
) -> None:
    """Test that a cut-off export raises the backend's error."""
    error = backend.RemoteProtocolError("peer closed connection")
    handler = fail_with(backend, error, received)
    documents = make_documents(backend, fake_config, handler)
    lines: typing.List[str] = []

    with documents.export_stream() as stream:
        with pytest.raises(backend.RemoteProtocolError):
            for line in stream:
                lines.append(line)

    assert lines == ['{"id":"1"}']


def test_truncated_body_raises_from_iter_bytes(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that the bytes view reports a cut-off export too."""
    error = backend.RemoteProtocolError("peer closed connection")
    documents = make_documents(backend, fake_config, fail_with(backend, error, b"a"))

    with documents.export_stream() as stream:
        with pytest.raises(backend.RemoteProtocolError):
            list(stream.iter_bytes())


def test_reading_after_a_failure_does_not_look_complete(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that lines and bytes keep raising once a read has failed."""
    error = backend.ReadError("connection reset")
    handler = fail_with(backend, error, b"a\n")
    documents = make_documents(backend, fake_config, handler)

    with documents.export_stream() as stream:
        assert next(stream) == "a"
        with pytest.raises(backend.ReadError):
            next(stream)
        with pytest.raises(TypesenseClientError, match="Start a new export"):
            next(stream)

    with documents.export_stream() as stream:
        chunks = stream.iter_bytes()
        assert next(chunks) == b"a\n"
        with pytest.raises(backend.ReadError):
            next(chunks)
        with pytest.raises(TypesenseClientError, match="Start a new export"):
            next(chunks)


def test_iteration_can_stop_and_carry_on(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that leaving a loop keeps the connection and the position."""
    handler = respond_with(backend, b"a\nb\n", b"c\n")
    documents = make_documents(backend, fake_config, handler)

    with documents.export_stream() as stream:
        for line in stream:
            assert line == "a"
            break
        assert not stream.response.is_closed
        assert list(stream) == ["b", "c"]


def test_closing_early_closes_the_response_without_draining(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that the rest of the body is not read."""
    sent: typing.List[int] = []

    def body() -> typing.Iterator[bytes]:
        for index in range(1000):
            sent.append(index)
            yield b"a\n"

    def handler(request: RequestType) -> ResponseType:
        return backend.Response(200, content=body())

    documents = make_documents(backend, fake_config, handler)

    with documents.export_stream() as stream:
        next(stream)

    assert stream.response.is_closed
    assert len(sent) == 1


def test_a_request_inside_the_loop_does_not_wait_for_the_export(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that a reading export holds no concurrency slot."""

    def handler(request: RequestType) -> ResponseType:
        if request.url.path == EXPORT_PATH:
            return backend.Response(200, content=chunked(BODY))
        return backend.Response(200, json={"name": "books"})

    fake_config.max_concurrent_requests = 1
    api_call = make_api_call(backend, fake_config, handler)
    documents = Documents[DocumentSchema](api_call, "books")

    with documents.export_stream() as stream:
        for _ in stream:
            request = Background(lambda: api_call.get("/collections/books", dict))
            assert request.result() == {"name": "books"}


def test_opening_an_export_takes_a_concurrency_slot(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that a request waits while an export is waiting for its headers."""
    export_started = threading.Event()
    send_headers = threading.Event()

    def handler(request: RequestType) -> ResponseType:
        if request.url.path == EXPORT_PATH:
            export_started.set()
            assert send_headers.wait(WAIT_SECONDS)
            return backend.Response(200, content=BODY)
        return backend.Response(200, json={})

    fake_config.max_concurrent_requests = 1
    api_call = make_api_call(backend, fake_config, handler)
    documents = Documents[DocumentSchema](api_call, "books")

    opening = Background(documents.export_stream)
    assert export_started.wait(WAIT_SECONDS)
    request = Background(lambda: api_call.get("/collections/books", dict))
    request.assert_waiting()

    send_headers.set()
    stream = opening.result()
    request.result()
    stream.close()


def test_only_one_view_of_the_body_can_be_read(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that asking for a second view raises at the call."""
    documents = make_documents(backend, fake_config, respond_with(backend, BODY))

    with documents.export_stream() as stream:
        next(stream)
        with pytest.raises(TypesenseClientError, match="already being read"):
            stream.iter_bytes()

    with documents.export_stream() as stream:
        stream.iter_bytes()
        with pytest.raises(TypesenseClientError, match="already being read"):
            iter(stream)
        with pytest.raises(TypesenseClientError, match="already being read"):
            stream.iter_bytes()


def test_error_responses_raise_when_opening(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that the error body is read and the request is not retried."""
    requests: typing.List[RequestType] = []

    def handler(request: RequestType) -> ResponseType:
        requests.append(request)
        return backend.Response(400, json={"message": "Bad filter"})

    documents = make_documents(backend, fake_config, handler)

    with pytest.raises(RequestMalformed, match="Bad filter"):
        documents.export_stream({"filter_by": "nope"})

    assert len(requests) == 1


def test_fails_over_before_the_body_starts(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that a 5xx is retried on the next node, which is marked healthy."""
    hosts: typing.List[str] = []

    def handler(request: RequestType) -> ResponseType:
        hosts.append(request.url.host)
        if request.url.host == "nearest":
            return backend.Response(503, text="Down")
        return backend.Response(200, content=BODY)

    documents = make_documents(backend, fake_config, handler)
    node = documents.api_call.node_manager.nodes[0]
    node.healthy = False
    node.last_access_ts = 0

    assert read_lines(documents) == LINES

    assert hosts == ["nearest", "node0"]
    assert fake_config.nearest_node is not None
    assert fake_config.nearest_node.healthy is False
    assert node.healthy is True


def test_does_not_retry_once_the_body_has_started(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that an error after the first chunk reaches the caller."""
    requests: typing.List[RequestType] = []

    def handler(request: RequestType) -> ResponseType:
        requests.append(request)
        error = backend.ReadError("connection reset")
        return backend.Response(200, content=chunked(b"a\n", error=error))

    documents = make_documents(backend, fake_config, handler)

    with documents.export_stream() as stream:
        assert next(stream) == "a"
        with pytest.raises(backend.ReadError):
            next(stream)

    assert len(requests) == 1


def test_reading_after_close_raises(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that a closed export cannot be mistaken for a finished one."""
    documents = make_documents(backend, fake_config, respond_with(backend, BODY))

    with documents.export_stream() as stream:
        next(stream)
    with pytest.raises(TypesenseClientError, match="closed"):
        next(stream)
    with pytest.raises(TypesenseClientError, match="closed"):
        iter(stream)
    with pytest.raises(TypesenseClientError, match="closed"):
        stream.iter_bytes()

    with documents.export_stream() as stream:
        chunks = stream.iter_bytes()
    with pytest.raises(TypesenseClientError, match="closed"):
        next(chunks)


def test_closing_while_another_thread_reads(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that closing does not raise and the reader does not see a clean end."""
    end_body = threading.Event()

    def body() -> typing.Iterator[bytes]:
        yield b"a\n"
        assert end_body.wait(WAIT_SECONDS)

    def handler(request: RequestType) -> ResponseType:
        return backend.Response(200, content=body())

    documents = make_documents(backend, fake_config, handler)
    stream = documents.export_stream()
    assert next(stream) == "a"
    reader = Background(lambda: next(stream))
    reader.assert_waiting()

    Background(stream.close).result()

    end_body.set()
    with pytest.raises(TypesenseClientError, match="closed"):
        reader.result()


def test_a_read_broken_by_closing_reports_the_close(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that the error a close causes does not look like a network failure."""
    break_read = threading.Event()

    def body() -> typing.Iterator[bytes]:
        yield b"a"
        assert break_read.wait(WAIT_SECONDS)
        raise backend.ReadError("connection closed")

    def handler(request: RequestType) -> ResponseType:
        return backend.Response(200, content=body())

    documents = make_documents(backend, fake_config, handler)
    stream = documents.export_stream()
    chunks = stream.iter_bytes()
    assert next(chunks) == b"a"
    reader = Background(lambda: next(chunks))
    reader.assert_waiting()

    Background(stream.close).result()
    break_read.set()

    with pytest.raises(TypesenseClientError, match="closed"):
        reader.result()
    with pytest.raises(TypesenseClientError, match="closed"):
        next(chunks)


def test_chunks_arriving_during_close_are_the_last_ones(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that the bytes view stops at the read that was already in progress."""
    send_more = threading.Event()

    def body() -> typing.Iterator[bytes]:
        yield b"a"
        assert send_more.wait(WAIT_SECONDS)
        yield b"b"
        yield b"c"

    def handler(request: RequestType) -> ResponseType:
        return backend.Response(200, content=body())

    documents = make_documents(backend, fake_config, handler)
    stream = documents.export_stream()
    chunks = stream.iter_bytes()
    assert next(chunks) == b"a"
    reader = Background(lambda: next(chunks))
    reader.assert_waiting()

    Background(stream.close).result()
    send_more.set()

    assert reader.result() == b"b"
    with pytest.raises(TypesenseClientError, match="closed"):
        next(chunks)


@pytest.mark.parametrize(
    ("max_connections", "max_concurrent_requests", "places"),
    [(3, 2, 1), (5, 2, 3), (2, 2, 1), (1, 5, 1)],
)
def test_open_exports_are_limited(
    fake_config: Configuration,
    max_connections: int,
    max_concurrent_requests: int,
    places: int,
) -> None:
    """Test the limit, including when the slots leave no room in the pool."""
    documents = limited_documents(fake_config, max_connections, max_concurrent_requests)

    with respx.mock:
        mock_export()
        streams = [open_export(documents) for _ in range(places)]
        waiting = Background(documents.export_stream)
        waiting.assert_waiting()

        streams[0].close()
        streams[0] = waiting.result()

        for stream in streams:
            stream.close()


def test_an_export_waiting_for_a_place_holds_no_slot(
    fake_config: Configuration,
) -> None:
    """Test that requests keep running while an export waits its turn."""
    documents = limited_documents(fake_config, 2, 1)

    with respx.mock:
        mock_export()
        respx.get(COLLECTION_URL).mock(return_value=httpx.Response(200, json={}))
        stream = open_export(documents)
        waiting = Background(documents.export_stream)
        waiting.assert_waiting()

        Background(lambda: documents.api_call.get(COLLECTION_PATH, dict)).result()

        stream.close()
        waiting.result().close()


def test_closing_twice_gives_back_one_place(fake_config: Configuration) -> None:
    """Test that a second close cannot raise the limit."""
    documents = limited_documents(fake_config, 3, 2)

    with respx.mock:
        mock_export()
        stream = open_export(documents)
        stream.close()
        stream.close()

        first = open_export(documents)
        second = Background(documents.export_stream)
        second.assert_waiting()
        first.close()
        second.result().close()


def test_overlapping_closes_keep_the_place_until_the_response_closes(
    fake_config: Configuration,
) -> None:
    """Test that a second close cannot free the place while the first is closing."""
    finish_close = threading.Event()

    class SlowToClose(httpx.SyncByteStream):
        """A body whose connection takes a while to close."""

        def __iter__(self) -> typing.Iterator[bytes]:
            """Yield the whole body."""
            yield BODY

        def close(self) -> None:
            """Wait until the test lets the close finish."""
            assert finish_close.wait(WAIT_SECONDS)

    documents = limited_documents(fake_config, 2, 1)

    with respx.mock:

        def respond(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, stream=SlowToClose())

        respx.get(EXPORT_URL).mock(side_effect=respond)
        stream = open_export(documents)
        first_close = Background(stream.close)
        first_close.assert_waiting()
        Background(stream.close).result()

        opening = Background(documents.export_stream)
        opening.assert_waiting()

        finish_close.set()
        first_close.result()
        opening.result().close()


def test_exports_are_not_limited_without_a_concurrency_limit(
    fake_config: Configuration,
) -> None:
    """Test that the limit needs ``max_concurrent_requests``."""
    documents = limited_documents(fake_config, 1, None)

    with respx.mock:
        mock_export()
        streams = [open_export(documents) for _ in range(3)]
        for stream in streams:
            stream.close()


def test_exports_are_not_limited_with_an_unlimited_pool(
    fake_config: Configuration,
) -> None:
    """Test that a pool without a size leaves nothing to reserve."""
    documents = limited_documents(fake_config, None, 2)

    with respx.mock:
        mock_export()
        streams = [open_export(documents) for _ in range(3)]
        for stream in streams:
            stream.close()


def test_reading_to_the_end_gives_back_the_place(
    fake_config: Configuration,
) -> None:
    """Test that an export read to its end does not need closing."""
    documents = limited_documents(fake_config, 3, 2)

    with respx.mock:
        mock_export()
        lines_stream = open_export(documents)
        lines = list(lines_stream)
        bytes_stream = open_export(documents)
        body = b"".join(bytes_stream.iter_bytes())
        open_export(documents).close()

    assert lines == LINES
    assert body == BODY


def test_a_failed_read_gives_back_the_place(fake_config: Configuration) -> None:
    """Test that an export that failed does not need closing."""
    documents = limited_documents(fake_config, 3, 2)

    with respx.mock:

        def respond(request: httpx.Request) -> httpx.Response:
            error = httpx.ReadError("connection reset")
            return httpx.Response(200, content=chunked(b"a\n", error=error))

        route = respx.get(EXPORT_URL).mock(side_effect=respond)
        stream = open_export(documents)
        with pytest.raises(httpx.ReadError):
            list(stream)

        route.mock(side_effect=export_response)
        open_export(documents).close()


def test_exports_are_not_limited_with_a_caller_supplied_client(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that the limit is skipped when the pool size is unknown."""
    fake_config.max_connections = 2
    fake_config.max_concurrent_requests = 1
    documents = make_documents(backend, fake_config, respond_with(backend, BODY))

    streams = [open_export(documents) for _ in range(3)]

    for stream in streams:
        stream.close()


def test_a_failed_open_gives_back_its_slot_and_place(
    fake_config: Configuration,
) -> None:
    """Test that an error response leaves the next export free to open."""
    documents = limited_documents(fake_config, 2, 1)

    with respx.mock:
        route = respx.get(EXPORT_URL)
        route.mock(return_value=httpx.Response(404, json={"message": "Not found"}))
        with pytest.raises(ObjectNotFound, match="Not found"):
            documents.export_stream()

        mock_export()
        open_export(documents).close()


def test_export_stream_through_the_default_client(
    fake_config: Configuration,
) -> None:
    """Test the export without a client passed in."""
    documents = Documents[DocumentSchema](ApiCall(fake_config), "books")

    with respx.mock:
        mock_export()
        assert read_lines(documents) == LINES
