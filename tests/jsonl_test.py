"""Tests for splitting an export body into lines."""

import json
import sys

import pytest

from typesense.jsonl import JSONLSplitter

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing


def split(chunks: typing.Iterable[bytes]) -> typing.List[bytes]:
    """Return every line in ``chunks``, including an unterminated last line."""
    splitter = JSONLSplitter()
    lines: typing.List[bytes] = []
    for chunk in chunks:
        lines.extend(splitter.feed(chunk))
    lines.extend(splitter.flush())
    return lines


def test_splits_on_line_feeds() -> None:
    """Test that each line is returned without its line feed."""
    assert split([b'{"id":"1"}\n{"id":"2"}\n']) == [b'{"id":"1"}', b'{"id":"2"}']


def test_keeps_an_unterminated_last_line_until_flush() -> None:
    """Test that the last line is held back, since more of it may still arrive."""
    splitter = JSONLSplitter()

    assert splitter.feed(b'{"id":"1"}\n{"id"') == [b'{"id":"1"}']
    assert splitter.flush() == [b'{"id"']
    assert splitter.flush() == []


def test_joins_a_line_split_across_chunks() -> None:
    """Test that the pieces of a line are joined, including at the line feed."""
    assert split([b"ab", b"cd", b"\nef", b"\n"]) == [b"abcd", b"ef"]


def test_ignores_empty_chunks() -> None:
    """Test that an empty chunk neither ends a line nor adds to it."""
    assert split([b"", b"ab", b"", b"c\n", b""]) == [b"abc"]


def test_keeps_blank_lines() -> None:
    """Test that lines are not filtered."""
    assert split([b"a\n\n\nb\n"]) == [b"a", b"", b"", b"b"]


def test_only_line_feeds_end_a_line() -> None:
    """Test that a carriage return stays in the line, alone or before a line feed."""
    assert split([b"a\rb\nc\r\n"]) == [b"a\rb", b"c\r"]


def test_a_final_line_feed_adds_no_empty_line() -> None:
    """Test that a body ending in a line feed has nothing left to flush."""
    splitter = JSONLSplitter()

    assert splitter.feed(b"a\n") == [b"a"]
    assert splitter.flush() == []


@pytest.mark.parametrize("separator", [" ", " ", "\u0085"])
def test_unicode_line_separators_stay_inside_a_line(separator: str) -> None:
    """Test that a body split at every byte offset gives back the same documents."""
    documents = [{"id": "1", "title": f"a{separator}b"}, {"id": "2", "title": "é"}]
    body = "\n".join(json.dumps(doc, ensure_ascii=False) for doc in documents).encode()

    for offset in range(len(body) + 1):
        lines = split([body[:offset], body[offset:]])
        assert [json.loads(line) for line in lines] == documents
