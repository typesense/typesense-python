"""Builders for the server-sent event streams Typesense sends."""

import json
import sys

import httpx

from typesense.types.document import MessageChunk

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

SEARCH_URL: typing.Final = "http://nearest:8108/collections/books/documents/search"
MULTI_SEARCH_URL: typing.Final = "http://nearest:8108/multi_search"

CONVERSATION_ID: typing.Final = "6f1c0e5a"

CHUNKS: typing.Final[typing.List[MessageChunk]] = [
    {"conversation_id": CONVERSATION_ID, "message": "The"},
    {"conversation_id": CONVERSATION_ID, "message": " Hobbit was"},
    {"conversation_id": CONVERSATION_ID, "message": " written by Tolkien."},
]

FINAL_RESPONSE: typing.Final[typing.Dict[str, typing.Any]] = {
    "conversation": {
        "answer": "The Hobbit was written by Tolkien.",
        "conversation_history": {"conversation": []},
        "conversation_id": CONVERSATION_ID,
        "query": "who wrote it",
    },
    "facet_counts": [],
    "found": 1,
    "hits": [{"document": {"id": "0", "title": "The Hobbit"}}],
    "out_of": 1,
    "page": 1,
    "search_time_ms": 2,
}


def sse_body(
    chunks: typing.Sequence[MessageChunk],
    final_response: typing.Optional[typing.Mapping[str, typing.Any]] = None,
) -> bytes:
    """
    Build a stream like Typesense's: the answer pieces, ``[DONE]``, then the response.

    Args:
        chunks (Sequence[MessageChunk]): The answer pieces.
        final_response (Mapping | None): The search response, or ``None`` to end
            the stream after the answer pieces.

    Returns:
        bytes: The response body.
    """
    events = [json.dumps(chunk) for chunk in chunks]
    if final_response is not None:
        events.extend(["[DONE]", json.dumps(final_response)])
    return "".join(f"data: {event}\n\n" for event in events).encode()


def sse_response(
    body: typing.Union[
        bytes, typing.Iterator[bytes], typing.AsyncIterator[bytes], None
    ] = None,
    final_response: typing.Mapping[str, typing.Any] = FINAL_RESPONSE,
) -> httpx.Response:
    """
    Build a ``text/event-stream`` response, by default the full search stream.

    Args:
        body (bytes | Iterator[bytes] | AsyncIterator[bytes] | None): The body,
            or ``None`` for the answer pieces followed by ``final_response``.
        final_response (Mapping): The search response sent after the answer.

    Returns:
        httpx.Response: The response.
    """
    return httpx.Response(
        200,
        headers={"Content-Type": "text/event-stream; charset=utf-8"},
        content=sse_body(CHUNKS, final_response) if body is None else body,
    )
