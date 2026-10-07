"""Types for multi-search."""

import sys

from typesense.types.document import (
    Conversation,
    MultiSearchParameters,
    SearchResponse,
)

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing


class MultiSearchResponse(typing.TypedDict):
    """
    Response schema for multi-search.

    Attributes:
        results (list[SearchResponse]): The search results.
        conversation (Conversation): The LLM's answer, for a conversational search.
    """

    results: typing.List[SearchResponse[typing.Any]]  # noqa: WPS110
    conversation: typing.NotRequired[Conversation]


class MultiSearchRequestSchema(typing.TypedDict):
    """
    Schema for multi-search request.

    Attributes:
        searches (list[MultiSearchParameters]): The search parameters.
    """

    union: typing.NotRequired[typing.Literal[True]]
    searches: typing.List[MultiSearchParameters]
