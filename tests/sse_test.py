"""Tests for the server-sent events decoder."""

import typing

import pytest

from typesense.sse import SSEDecoder, ServerSentEvent, aiter_events, iter_events


def decode(*chunks: bytes) -> list[ServerSentEvent]:
    """Decode the chunks with a fresh decoder."""
    return list(iter_events(chunks, SSEDecoder()))


@pytest.mark.parametrize("line_end", [b"\n", b"\r\n", b"\r"])
def test_line_endings(line_end: bytes) -> None:
    """Test that LF, CRLF and a lone CR all end a line."""
    body = b"data: one" + line_end + line_end + b"data: two" + line_end + line_end

    assert [event.data for event in decode(body)] == ["one", "two"]


def test_crlf_split_across_chunks() -> None:
    """Test that a CRLF split across two reads is a single line end."""
    events = decode(b"data: one\r", b"\n\r", b"\ndata: two\r\n\r\n")

    assert [event.data for event in events] == ["one", "two"]


def test_multibyte_character_split_across_chunks() -> None:
    """Test that a UTF-8 character split across two reads is decoded intact."""
    body = 'data: {"message": "καλημέρα"}\n\n'.encode()
    split_at = body.index("μ".encode()) + 1

    events = decode(body[:split_at], body[split_at:])

    assert events[0].json() == {"message": "καλημέρα"}


def test_unicode_line_separator_inside_data() -> None:
    """Test that U+2028 inside JSON does not split the line."""
    events = decode('data: {"message": "a b"}\n\n'.encode())

    assert events[0].json() == {"message": "a b"}


def test_multiline_data_is_joined_with_newlines() -> None:
    """Test that the data lines of one event are joined with a newline."""
    events = decode(b"data: first\ndata:second\n\n")

    assert events[0].data == "first\nsecond"


def test_only_one_leading_space_is_stripped() -> None:
    """Test that a single space after the colon is removed, but not more."""
    assert decode(b"data:  padded\n\n")[0].data == " padded"


def test_comments_and_unknown_fields_are_ignored() -> None:
    """Test that comment lines and unknown fields do not create events."""
    events = decode(b": keep-alive\n\nfoo: bar\ndata: real\n\n")

    assert [event.data for event in events] == ["real"]


def test_event_id_and_retry_fields() -> None:
    """Test that event, id and retry are parsed, and id carries over."""
    events = decode(
        b"event: delta\nid: 7\nretry: 1500\ndata: a\n\ndata: b\n\nretry: x1\ndata: c\n\n",
    )

    assert events == [
        ServerSentEvent(event="delta", data="a", id="7", retry=1500),
        ServerSentEvent(event="message", data="b", id="7"),
        ServerSentEvent(event="message", data="c", id="7"),
    ]


def test_leading_bom_is_stripped() -> None:
    """Test that a UTF-8 byte order mark at the start of the stream is ignored."""
    assert decode(b"\xef\xbb\xbfdata: x\n\n")[0].data == "x"


def test_trailing_event_without_blank_line_is_dropped() -> None:
    """Test that an unterminated event is not dispatched, and its text is kept."""
    decoder = SSEDecoder()

    events = list(iter_events([b"data: one\n\n", b'{"message": "boom"}'], decoder))

    assert [event.data for event in events] == ["one"]
    assert decoder.remainder == '{"message": "boom"}'


def test_event_without_data_is_not_dispatched() -> None:
    """Test that a blank line after only non-data fields dispatches nothing."""
    assert decode(b"event: ping\n\n") == []


def test_byte_at_a_time() -> None:
    """Test decoding when every read returns a single byte."""
    body = b'data: {"message": "hi"}\r\n\r\ndata: [DONE]\r\n\r\n'

    events = decode(*(body[index : index + 1] for index in range(len(body))))

    assert [event.data for event in events] == ['{"message": "hi"}', "[DONE]"]


async def test_aiter_events() -> None:
    """Test the async entry point."""

    async def chunks() -> typing.AsyncIterator[bytes]:
        for chunk in (b"data: a\n", b"\ndata: b\n\n"):
            yield chunk

    events = [event.data async for event in aiter_events(chunks(), SSEDecoder())]

    assert events == ["a", "b"]
