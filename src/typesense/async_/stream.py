"""
Streamed conversational search responses and document exports.

With ``conversation_stream`` enabled, Typesense sends the LLM's answer as
server-sent events while it is generated, then the full search response:

    data: {"conversation_id": "...", "message": "The"}
    data: {"conversation_id": "...", "message": " answer"}
    data: [DONE]
    data: {"conversation": {...}, "hits": [...], ...}

``AsyncSearchStream`` yields the answer pieces as ``MessageChunk`` dicts and keeps
the final event as the search response, returned by ``get_final_response``.

``AsyncExportStream`` reads a document export, one JSONL line or one chunk of bytes
at a time, so that a large collection never has to fit in memory.
"""

import sys
from collections import deque
from contextlib import AsyncExitStack
from types import TracebackType

from typesense.exceptions import TypesenseClientError
from typesense.http_backend import ResponseType
from typesense.jsonl import JSONLSplitter
from typesense.sse import SSEDecoder, ServerSentEvent, aiter_events
from typesense.types.document import MessageChunk, StreamConfig, StreamConfigBuilder

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

TFinal = typing.TypeVar("TFinal")

_DONE = "[DONE]"

_EXPORT_CLOSED = "This export stream is closed."
_EXPORT_FAILED = "This export stream failed while reading. Start a new export."
_EXPORT_CLAIMED = (
    "This export stream is already being read. Read its lines or its bytes, not both."
)


class AsyncSearchStream(typing.Generic[TFinal]):
    """
    An open streaming search response.

    Iterate over it for the pieces of the LLM's answer, then call
    ``get_final_response`` for the full search response. Use it as a context
    manager, or call ``aclose``, to release the connection if you stop early.

    Attributes:
        response (httpx.Response | httpx2.Response): The underlying response.
    """

    def __init__(
        self,
        response: ResponseType,
        exit_stack: AsyncExitStack,
    ) -> None:
        """
        Initialize the stream.

        Args:
            response (httpx.Response | httpx2.Response): A successful response
                opened with ``stream=True``.
            exit_stack (AsyncExitStack): Closes the response and releases the
                request's concurrency slot when the stream is closed.
        """
        self.response = response
        self._exit_stack = exit_stack
        self._closed = False
        self._final: typing.Optional[TFinal] = None
        self._decoder = SSEDecoder()
        self._iterator = self._iter_chunks()

    def __aiter__(self) -> typing.Self:
        """Return the stream itself; it can be iterated only once."""
        return self

    async def __anext__(self) -> MessageChunk:
        """Return the next piece of the answer."""
        return await self._iterator.__anext__()

    async def __aenter__(self) -> typing.Self:
        """Enter the context manager."""
        return self

    async def __aexit__(
        self,
        exc_type: typing.Optional[typing.Type[BaseException]],
        exc_val: typing.Optional[BaseException],
        exc_tb: typing.Optional[TracebackType],
    ) -> None:
        """Close the stream."""
        await self.aclose()

    async def get_final_response(self) -> TFinal:
        """
        Read the rest of the stream and return the full search response.

        Returns:
            TFinal: The search response sent after the answer.

        Raises:
            TypesenseClientError: If the stream was closed or ended before the
                search response arrived.
        """
        if self._final is None and self._closed:
            raise TypesenseClientError(
                "The stream was closed before the search response arrived.",
            )
        async for _ in self:
            pass
        if self._final is None:
            raise TypesenseClientError(self._missing_final_message())
        return self._final

    async def aclose(self) -> None:
        """Close the response and release its connection."""
        await self._iterator.aclose()
        await self._close_response()

    async def _close_response(self) -> None:
        """Close the response and release its concurrency slot, once."""
        if self._closed:
            return
        self._closed = True
        await self._exit_stack.aclose()

    async def _iter_chunks(self) -> typing.AsyncGenerator[MessageChunk, None]:
        """Yield the answer pieces and keep the final search response."""
        try:
            if "event-stream" not in self.response.headers.get("Content-Type", ""):
                # Typesense answers with plain JSON when the LLM is never called,
                # e.g. when every search of a multi-search fails.
                await self.response.aread()
                self._final = typing.cast(TFinal, self.response.json())
                return
            async for event in aiter_events(self.response.aiter_bytes(), self._decoder):
                chunk = self._handle_event(event)
                if chunk is not None:
                    yield chunk
            if self._final is None:
                raise TypesenseClientError(self._missing_final_message())
        finally:
            await self._close_response()

    def _handle_event(self, event: ServerSentEvent) -> typing.Optional[MessageChunk]:
        """Return the event's answer piece, or keep it as the final response."""
        if event.data == _DONE:
            return None
        try:
            payload = event.json()
        except ValueError as json_error:
            raise TypesenseClientError(
                f"Invalid event in stream: {event.data}",
            ) from json_error
        if not isinstance(payload, dict):
            return None
        if any(key in payload for key in ("hits", "grouped_hits", "results")):
            self._final = typing.cast(TFinal, payload)
            return None
        if "conversation_id" in payload and "message" in payload:
            return MessageChunk(
                conversation_id=payload["conversation_id"],
                message=payload["message"],
            )
        if "message" in payload:
            raise TypesenseClientError(payload["message"])
        return None

    def _missing_final_message(self) -> str:
        """Describe a stream that ended without the search response."""
        message = "The stream ended before the search response arrived."
        remainder = self._decoder.remainder.strip()
        return f"{message} {remainder}" if remainder else message


class AsyncExportChunks:
    """
    The decoded bytes of an export, returned by ``AsyncExportStream.aiter_bytes``.

    An httpx iterator simply ends once it has been closed or has failed, which would
    make a partial export look complete. Reading from this one raises instead.
    """

    def __init__(
        self,
        chunks: typing.AsyncIterator[bytes],
        exit_stack: AsyncExitStack,
    ) -> None:
        """
        Initialize the iterator.

        Args:
            chunks: The response's decoded bytes. Holding on to this iterator
                matters, because dropping it closes the connection.
            exit_stack (AsyncExitStack): Closes the response and gives up the
                export's place once the body has ended or failed.
        """
        self._chunks = chunks
        self._exit_stack = exit_stack
        self._unreadable: typing.Optional[str] = None

    def __aiter__(self) -> typing.Self:
        """Return the iterator itself; it can be iterated only once."""
        return self

    async def __anext__(self) -> bytes:
        """Return the next chunk of the body."""
        self._raise_if_unreadable()
        try:
            return await self._chunks.__anext__()
        except BaseException as error:
            if isinstance(error, Exception):
                # Closing the stream ends or breaks a read that is in progress.
                self._raise_if_unreadable()
            if isinstance(error, StopAsyncIteration):
                await self._exit_stack.aclose()
            else:
                await self._fail()
            raise

    async def _fail(self) -> None:
        """Make further reads raise, and give up the export's place."""
        self._unreadable = self._unreadable or _EXPORT_FAILED
        await self._exit_stack.aclose()

    def _mark_closed(self) -> None:
        """Make further reads raise."""
        self._unreadable = _EXPORT_CLOSED

    def _raise_if_unreadable(self) -> None:
        """Raise if the stream was closed or a read has failed."""
        if self._unreadable is not None:
            raise TypesenseClientError(self._unreadable)


class AsyncExportStream:
    """
    An open document export.

    Iterate over it for the raw JSONL lines, as ``str`` without the line feed, or
    call ``aiter_bytes`` for the decoded bytes. An export can be read only one of
    these ways, and only once. Use it as a context manager, or call ``aclose``:
    a stream abandoned before its end keeps its place among the open exports.

    Errors while reading are raised as they are, from httpx or httpx2, and nothing
    is retried. A failed export has to be started again.

    Attributes:
        response (httpx.Response | httpx2.Response): The underlying response.
    """

    def __init__(
        self,
        response: ResponseType,
        exit_stack: AsyncExitStack,
    ) -> None:
        """
        Initialize the stream.

        Args:
            response (httpx.Response | httpx2.Response): A successful response
                opened with ``stream=True``.
            exit_stack (AsyncExitStack): Closes the response and gives up the
                export's place when the stream is closed or its body ends or fails.
        """
        self.response = response
        self._exit_stack = exit_stack
        self._closed = False
        self._chunks: typing.Optional[AsyncExportChunks] = None
        self._line_chunks: typing.Optional[AsyncExportChunks] = None
        self._splitter = JSONLSplitter()
        self._lines: typing.Deque[bytes] = deque()

    def __aiter__(self) -> typing.Self:
        """Start reading lines, or carry on from the last line read."""
        self._claim_lines()
        return self

    async def __anext__(self) -> str:
        """Return the next line, without its line feed."""
        chunks = self._claim_lines()
        while not self._lines:
            try:
                chunk = await chunks.__anext__()
            except StopAsyncIteration:
                # Only a complete body gets here, so this is a whole last line.
                self._lines.extend(self._splitter.flush())
                if not self._lines:
                    raise
            else:
                self._lines.extend(self._splitter.feed(chunk))
        line = self._lines.popleft()
        try:
            return line.decode("utf-8")
        except UnicodeDecodeError:
            # Dropping the lines already read makes every further read raise.
            self._lines.clear()
            await chunks._fail()
            raise

    async def __aenter__(self) -> typing.Self:
        """Enter the context manager."""
        return self

    async def __aexit__(
        self,
        exc_type: typing.Optional[typing.Type[BaseException]],
        exc_val: typing.Optional[BaseException],
        exc_tb: typing.Optional[TracebackType],
    ) -> None:
        """Close the stream."""
        await self.aclose()

    def aiter_bytes(
        self,
        chunk_size: typing.Optional[int] = None,
    ) -> AsyncExportChunks:
        """
        Read the export as bytes, for example to write it to a file.

        Args:
            chunk_size (int | None): The size of each chunk. Defaults to the sizes
                the data arrives in.

        Returns:
            AsyncExportChunks: The decoded bytes of the export.

        Raises:
            TypesenseClientError: If the stream is closed or already being read.
        """
        return self._claim_chunks(chunk_size)

    async def aclose(self) -> None:
        """Close the response without reading the rest of it. Safe to call twice."""
        self._closed = True
        if self._chunks is not None:
            self._chunks._mark_closed()
        await self._exit_stack.aclose()

    def _claim_lines(self) -> AsyncExportChunks:
        """Return the chunks that lines are read from."""
        if self._closed:
            raise TypesenseClientError(_EXPORT_CLOSED)
        if self._line_chunks is None:
            self._line_chunks = self._claim_chunks(None)
        return self._line_chunks

    def _claim_chunks(self, chunk_size: typing.Optional[int]) -> AsyncExportChunks:
        """Start reading the body, which can be done only once."""
        if self._closed:
            raise TypesenseClientError(_EXPORT_CLOSED)
        if self._chunks is not None:
            raise TypesenseClientError(_EXPORT_CLAIMED)
        self._chunks = AsyncExportChunks(
            self.response.aiter_bytes(chunk_size),
            self._exit_stack,
        )
        return self._chunks


def resolve_stream_config(
    stream_config: typing.Union[
        StreamConfig[TFinal],
        StreamConfigBuilder[TFinal],
        None,
    ],
) -> typing.Optional[StreamConfig[TFinal]]:
    """Return the callbacks of a ``StreamConfig`` or ``StreamConfigBuilder``."""
    if isinstance(stream_config, StreamConfigBuilder):
        return stream_config.build()
    return stream_config


def notify_error(
    stream_config: typing.Optional[StreamConfig[TFinal]],
    error: BaseException,
) -> None:
    """Run the ``on_error`` callback, if there is one."""
    on_error = (stream_config or {}).get("on_error")
    if on_error is not None:
        on_error(error)


async def consume_stream(
    stream: AsyncSearchStream[TFinal],
    stream_config: typing.Optional[StreamConfig[TFinal]],
) -> TFinal:
    """
    Read a stream to the end, running the ``on_chunk`` and ``on_complete`` callbacks.

    Args:
        stream (AsyncSearchStream): The stream to read.
        stream_config (StreamConfig | None): The callbacks to run.

    Returns:
        TFinal: The full search response.
    """
    stream_config = stream_config or {}
    on_chunk = stream_config.get("on_chunk")
    async with stream:
        async for chunk in stream:
            if on_chunk is not None:
                on_chunk(chunk)
        final_response = await stream.get_final_response()
    on_complete = stream_config.get("on_complete")
    if on_complete is not None:
        on_complete(final_response)
    return final_response
