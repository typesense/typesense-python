"""
Server-sent events (SSE) parsing for streaming responses.

Typesense streams conversational search answers as ``text/event-stream``. This
module turns the raw response bytes into ``ServerSentEvent`` objects, following the
WHATWG parsing rules:

- Lines end with CRLF, LF or a lone CR, even when a CRLF pair is split across
  two network reads.
- Lines are split before decoding, so a multi-byte UTF-8 character split across
  reads stays intact, and characters like U+2028 inside JSON never break a line.
  (httpx's ``iter_lines`` splits on those, so it is not used here.)
- Multiple ``data:`` lines in one event are joined with ``\\n``.
- Lines starting with ``:`` are comments.
- An event is dispatched on a blank line; a trailing event without one is dropped.

``iter_events`` and ``aiter_events`` are the sync and async entry points
(``utils/run-unasync.py`` maps one name to the other).
"""

import json
import re
import sys

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

_LINE_END = re.compile(rb"\r\n|\r|\n")
_BOM = "﻿"


class ServerSentEvent:
    """A single dispatched server-sent event."""

    def __init__(
        self,
        *,
        event: str = "message",
        data: str = "",
        id: str = "",  # noqa: A002 (the SSE field name)
        retry: typing.Optional[int] = None,
    ) -> None:
        """
        Initialize the event.

        Args:
            event (str): The event type. Defaults to ``message``.
            data (str): The event data, with multiple ``data:`` lines joined by ``\\n``.
            id (str): The last event ID seen on the stream.
            retry (int | None): The reconnection time sent with the event, if any.
        """
        self.event = event
        self.data = data
        self.id = id
        self.retry = retry

    def json(self) -> typing.Any:
        """Parse the event data as JSON."""
        return json.loads(self.data)

    def __repr__(self) -> str:
        """Return a debug representation of the event."""
        return (
            f"ServerSentEvent(event={self.event!r}, data={self.data!r}, "
            f"id={self.id!r}, retry={self.retry!r})"
        )

    def __eq__(self, other: object) -> bool:
        """Compare two events field by field."""
        if not isinstance(other, ServerSentEvent):
            return NotImplemented
        return (self.event, self.data, self.id, self.retry) == (
            other.event,
            other.data,
            other.id,
            other.retry,
        )


class SSEDecoder:
    """Incremental decoder that turns response bytes into server-sent events."""

    def __init__(self) -> None:
        """Initialize an empty decoder."""
        self._buffer = b""
        # The previous chunk ended in ``\r``; a leading ``\n`` belongs to that line end.
        self._pending_cr = False
        self._at_start = True
        self._event = ""
        self._data: typing.List[str] = []
        self._last_event_id = ""
        self._retry: typing.Optional[int] = None

    @property
    def remainder(self) -> str:
        """Return the bytes after the last line end, decoded, once the stream is over."""
        return self._buffer.decode("utf-8", errors="replace")

    def feed(self, chunk: bytes) -> typing.List[ServerSentEvent]:
        """
        Decode a chunk of the response body.

        Args:
            chunk (bytes): The next bytes read from the response.

        Returns:
            List[ServerSentEvent]: The events completed by this chunk.
        """
        if not chunk:
            return []
        if self._pending_cr and chunk.startswith(b"\n"):
            chunk = chunk[1:]
        self._pending_cr = False

        buffer = self._buffer + chunk
        events: typing.List[ServerSentEvent] = []
        start = 0
        for line_end in _LINE_END.finditer(buffer):
            if line_end.group() == b"\r" and line_end.end() == len(buffer):
                self._pending_cr = True
            event = self._process_line(buffer[start : line_end.start()])
            if event is not None:
                events.append(event)
            start = line_end.end()
        self._buffer = buffer[start:]
        return events

    def _process_line(self, raw_line: bytes) -> typing.Optional[ServerSentEvent]:
        """Apply one line to the pending event, returning the event on a blank line."""
        line = raw_line.decode("utf-8", errors="replace")
        if self._at_start:
            self._at_start = False
            line = line[len(_BOM) :] if line.startswith(_BOM) else line

        if not line:
            return self._dispatch()
        if line.startswith(":"):
            return None

        field, _, field_value = line.partition(":")
        if field_value.startswith(" "):
            field_value = field_value[1:]

        if field == "event":
            self._event = field_value
        elif field == "data":
            self._data.append(field_value)
        elif field == "id":
            if "\0" not in field_value:
                self._last_event_id = field_value
        elif field == "retry":
            if field_value.isascii() and field_value.isdigit():
                self._retry = int(field_value)
        return None

    def _dispatch(self) -> typing.Optional[ServerSentEvent]:
        """Build the pending event and reset the per-event fields."""
        event: typing.Optional[ServerSentEvent] = None
        if self._data:
            event = ServerSentEvent(
                event=self._event or "message",
                data="\n".join(self._data),
                id=self._last_event_id,
                retry=self._retry,
            )
        self._event = ""
        self._data = []
        self._retry = None
        return event


def iter_events(
    chunks: typing.Iterable[bytes],
    decoder: SSEDecoder,
) -> typing.Iterator[ServerSentEvent]:
    """
    Yield the server-sent events in a stream of response bytes.

    Args:
        chunks (Iterable[bytes]): The response body, e.g. ``response.iter_bytes()``.
        decoder (SSEDecoder): The decoder holding the parsing state.

    Yields:
        ServerSentEvent: Each event, as soon as its blank line arrives.
    """
    for chunk in chunks:
        yield from decoder.feed(chunk)


async def aiter_events(
    chunks: typing.AsyncIterable[bytes],
    decoder: SSEDecoder,
) -> typing.AsyncIterator[ServerSentEvent]:
    """
    Yield the server-sent events in an async stream of response bytes.

    Args:
        chunks (AsyncIterable[bytes]): The response body, e.g. ``response.aiter_bytes()``.
        decoder (SSEDecoder): The decoder holding the parsing state.

    Yields:
        ServerSentEvent: Each event, as soon as its blank line arrives.
    """
    async for chunk in chunks:
        for event in decoder.feed(chunk):
            yield event
