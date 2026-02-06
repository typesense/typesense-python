"""
SSE stream parsing and chunk combining for conversation search streaming.

This module contains pure logic for parsing server-sent event lines from
conversation_stream responses and combining message chunks into a final
search response. Used by async API calls.
"""

import json
import sys

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

from typesense.types.document import MessageChunk

JSONPrimitive: typing.TypeAlias = typing.Union[str, int, float, bool, None]
JSONValue: typing.TypeAlias = typing.Union[
    JSONPrimitive, typing.Dict[str, "JSONValue"], typing.List["JSONValue"]
]
JSONDict: typing.TypeAlias = typing.Dict[str, JSONValue]

_SEARCH_RESPONSE_KEYS = frozenset(
    {"results", "found", "hits", "page", "search_time_ms"}
)

StreamChunk: typing.TypeAlias = typing.Union[MessageChunk, JSONDict]


def parse_sse_line(line: str) -> typing.Optional[StreamChunk]:
    """
    Parse a single SSE line into a MessageChunk, search response dict, or None.

    Handles:
    - Empty lines and "data: [DONE]" -> None
    - "data: {...}" -> parse JSON, return MessageChunk or search response
    - Raw JSON line starting with "{" -> same
    - Plain text -> return chunk with conversation_id="unknown", message=line

    Returns:
        MessageChunk for conversation chunks, dict for search responses, or None to skip.
    """
    line = line.strip()
    if not line or line == "data: [DONE]":
        return None

    # SSE format: "data: {...}"
    if line.startswith("data:"):
        content = line[5:].strip()
        return _parse_data_content(content)

    # Raw JSON
    if line.startswith("{"):
        return _parse_json_content(line)

    return _chunk_from_text(line)


def _parse_data_content(content: str) -> typing.Optional[StreamChunk]:
    """Parse the content after 'data:' into a MessageChunk, search response, or None."""
    if not content:
        return None
    if content.startswith("{"):
        return _parse_json_content(content)
    return _chunk_from_text(content)


def _parse_json_content(raw: str) -> StreamChunk:
    """Parse a JSON string into a MessageChunk or search response dict."""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return _chunk_from_text(raw)
    if not isinstance(data, dict):
        return _chunk_from_text(json.dumps(data))

    parsed = typing.cast(JSONDict, data)
    conversation_id = parsed.get("conversation_id")
    message = parsed.get("message")
    nested_conversation = parsed.get("conversation")

    if conversation_id is None or message is None:
        if isinstance(nested_conversation, dict):
            nested_conversation_id = nested_conversation.get("conversation_id")
            nested_message = nested_conversation.get("message")
            if conversation_id is None and nested_conversation_id is not None:
                conversation_id = nested_conversation_id
            if message is None and nested_message is not None:
                message = nested_message

    if conversation_id is None:
        parsed["conversation_id"] = "unknown"
    elif not isinstance(conversation_id, str):
        parsed["conversation_id"] = str(conversation_id)
    else:
        parsed["conversation_id"] = conversation_id

    if message is None:
        parsed["message"] = ""
    elif not isinstance(message, str):
        parsed["message"] = str(message)
    else:
        parsed["message"] = message

    return parsed


def _is_search_response_dict(data: typing.Mapping[str, JSONValue]) -> bool:
    """Check if a dict is a search response (has found, hits, results, etc.)."""
    return bool(set(data.keys()) & _SEARCH_RESPONSE_KEYS)


def is_message_chunk(chunk: JSONValue) -> bool:
    """Return True if chunk is a conversation message chunk (has conversation_id and message)."""
    if not isinstance(chunk, dict):
        return False
    if "message" not in chunk or "conversation_id" not in chunk:
        return False
    return not _is_search_response_dict(chunk)


def is_complete_search_response(chunk: JSONValue) -> bool:
    """Return True if chunk looks like a full search response (has hits, found, etc.)."""
    if not isinstance(chunk, dict) or not chunk:
        return False
    keys = set(chunk.keys())
    return bool(keys & _SEARCH_RESPONSE_KEYS)


def combine_stream_chunks(
    chunks: typing.Sequence[StreamChunk],
) -> JSONDict:
    """
    Combine streamed chunks into a single search response.

    - If no chunks, return empty dict.
    - If one chunk, return it.
    - If we have message chunks (conversation_id + message), find the metadata
      chunk (complete search response) and return it; otherwise return last chunk
      if it is complete.
    - For regular search streams, return the last chunk if it is a complete response.
    """
    if not chunks:
        return {}
    if len(chunks) == 1:
        return typing.cast(JSONDict, chunks[0])

    message_chunks = [c for c in chunks if is_message_chunk(c)]
    if message_chunks:
        for chunk in chunks:
            if is_complete_search_response(chunk):
                return typing.cast(JSONDict, chunk)
        return typing.cast(JSONDict, chunks[-1])

    last = chunks[-1]
    if is_complete_search_response(last):
        return typing.cast(JSONDict, last)
    return typing.cast(JSONDict, last)


def _chunk_from_text(text: str) -> MessageChunk:
    return {"conversation_id": "unknown", "message": text}
