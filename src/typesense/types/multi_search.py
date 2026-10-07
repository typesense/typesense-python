"""Types for multi-search."""

import sys

from typesense.types.document import MultiSearchParameters, SearchResponse

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing


class MultiSearchResponse(typing.TypedDict):
    """
    Response schema for multi-search.

    Attributes:
        results (list[SearchResponse]): The search results.
    """

    results: typing.List[SearchResponse[typing.Any]]  # noqa: WPS110


class MultiSearchRequestSchemaUnion(typing.TypedDict):
    """
    Schema for union multi-search request.

    Attributes:
        searches (list[MultiSearchParameters]): The search parameters.
    """

    union: typing.Literal[True]
    searches: typing.List[MultiSearchParameters]


class MultiSearchRequestSchemaMulti(typing.TypedDict):
    """
    Schema for standard multi-search request.

    Attributes:
        searches (list[MultiSearchParameters]): The search parameters.
    """

    union: typing.NotRequired[typing.Literal[False]]
    searches: typing.List[MultiSearchParameters]


MultiSearchRequestSchema = typing.Union[
    MultiSearchRequestSchemaUnion,
    MultiSearchRequestSchemaMulti,
]
MultiSearchResponseSchema = typing.Union[
    MultiSearchResponse,
    SearchResponse[typing.Any],
]
