"""
Streamed conversational search responses.

With ``conversation_stream`` enabled, Typesense sends the LLM's answer as
server-sent events while it is generated, then the full search response:

    data: {"conversation_id": "...", "message": "The"}
    data: {"conversation_id": "...", "message": " answer"}
    data: [DONE]
    data: {"conversation": {...}, "hits": [...], ...}

``SearchStream`` yields the answer pieces as ``MessageChunk`` dicts and keeps
the final event as the search response, returned by ``get_final_response``.
"""

import sys
from types import TracebackType

from typesense.exceptions import TypesenseClientError
from typesense.http_backend import ResponseType
from typesense.sse import SSEDecoder, ServerSentEvent, iter_events
from typesense.types.document import MessageChunk, StreamConfig, StreamConfigBuilder

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

TFinal = typing.TypeVar("TFinal")

_DONE = "[DONE]"


class SearchStream(typing.Generic[TFinal]):
    """
    An open streaming search response.

    Iterate over it for the pieces of the LLM's answer, then call
    ``get_final_response`` for the full search response. Use it as a context
    manager, or call ``close``, to release the connection if you stop early.

    Attributes:
        response (httpx.Response | httpx2.Response): The underlying response.
    """

    def __init__(
        self,
        response: ResponseType,
        on_close: typing.Callable[[], None],
    ) -> None:
        """
        Initialize the stream.

        Args:
            response (httpx.Response | httpx2.Response): A successful response
                opened with ``stream=True``.
            on_close (Callable[[], None]): Called once when the stream is closed,
                to release the request's concurrency slot.
        """
        self.response = response
        self._on_close = on_close
        self._closed = False
        self._final: typing.Optional[TFinal] = None
        self._decoder = SSEDecoder()
        self._iterator = self._iter_chunks()

    def __iter__(self) -> typing.Self:
        """Return the stream itself; it can be iterated only once."""
        return self

    def __next__(self) -> MessageChunk:
        """Return the next piece of the answer."""
        return self._iterator.__next__()

    def __enter__(self) -> typing.Self:
        """Enter the context manager."""
        return self

    def __exit__(
        self,
        exc_type: typing.Optional[typing.Type[BaseException]],
        exc_val: typing.Optional[BaseException],
        exc_tb: typing.Optional[TracebackType],
    ) -> None:
        """Close the stream."""
        self.close()

    def get_final_response(self) -> TFinal:
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
        for _ in self:
            pass
        if self._final is None:
            raise TypesenseClientError(self._missing_final_message())
        return self._final

    def close(self) -> None:
        """Close the response and release its connection."""
        self._iterator.close()
        self._close_response()

    def _close_response(self) -> None:
        """Close the response once, then run ``on_close``."""
        if self._closed:
            return
        self._closed = True
        try:
            self.response.close()
        finally:
            self._on_close()

    def _iter_chunks(self) -> typing.Generator[MessageChunk, None, None]:
        """Yield the answer pieces and keep the final search response."""
        try:
            if "event-stream" not in self.response.headers.get("Content-Type", ""):
                # Typesense answers with plain JSON when the LLM is never called,
                # e.g. when every search of a multi-search fails.
                self.response.read()
                self._final = typing.cast(TFinal, self.response.json())
                return
            for event in iter_events(self.response.iter_bytes(), self._decoder):
                chunk = self._handle_event(event)
                if chunk is not None:
                    yield chunk
            if self._final is None:
                raise TypesenseClientError(self._missing_final_message())
        finally:
            self._close_response()

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


def consume_stream(
    stream: SearchStream[TFinal],
    stream_config: typing.Optional[StreamConfig[TFinal]],
) -> TFinal:
    """
    Read a stream to the end, running the ``on_chunk`` and ``on_complete`` callbacks.

    Args:
        stream (SearchStream): The stream to read.
        stream_config (StreamConfig | None): The callbacks to run.

    Returns:
        TFinal: The full search response.
    """
    stream_config = stream_config or {}
    on_chunk = stream_config.get("on_chunk")
    with stream:
        for chunk in stream:
            if on_chunk is not None:
                on_chunk(chunk)
        final_response = stream.get_final_response()
    on_complete = stream_config.get("on_complete")
    if on_complete is not None:
        on_complete(final_response)
    return final_response
