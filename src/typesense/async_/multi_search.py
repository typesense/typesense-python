"""
This module provides async functionality for performing multi-search operations in the Typesense API.

It contains the AsyncMultiSearch class, which allows for executing multiple search queries
asynchronously in a single API call.

Classes:
    AsyncMultiSearch: Manages async multi-search operations in the Typesense API.

Dependencies:
    - typesense.async_api_call: Provides the AsyncApiCall class for making async API requests.
    - typesense.preprocess: Provides the stringify_search_params function for parameter processing.
    - typesense.types.document: Provides the MultiSearchCommonParameters type.
    - typesense.types.multi_search: Provides MultiSearchRequestSchema and MultiSearchResponse types.

Note: This module uses conditional imports to support both Python 3.11+ and earlier versions.
"""

import sys

from .api_call import AsyncApiCall
from typesense.preprocess import stringify_search_params
from typesense.types.document import MultiSearchCommonParameters, SearchResponse
from typesense.types.multi_search import (
    MultiSearchRequestSchema,
    MultiSearchRequestSchemaMulti,
    MultiSearchRequestSchemaUnion,
    MultiSearchResponse,
    MultiSearchResponseSchema,
)

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing


class AsyncMultiSearch:
    """
    Manages async multi-search operations in the Typesense API.

    This class provides async methods to perform multiple search queries in a single API call.

    Attributes:
        resource_path (str): The API endpoint path for multi-search operations.
        api_call (AsyncApiCall): The AsyncApiCall instance for making async API requests.
    """

    resource_path: typing.Final[str] = "/multi_search"

    def __init__(self, api_call: AsyncApiCall) -> None:
        """
        Initialize the AsyncMultiSearch instance.

        Args:
            api_call (AsyncApiCall): The AsyncApiCall instance for making async API requests.
        """
        self.api_call = api_call

    @typing.overload
    async def perform(
        self,
        search_queries: MultiSearchRequestSchemaUnion,
        common_params: typing.Union[MultiSearchCommonParameters, None] = None,
    ) -> SearchResponse[typing.Any]:
        """Perform a union multi-search operation."""

    @typing.overload
    async def perform( # type: ignore[overload-cannot-match]
        self,
        search_queries: MultiSearchRequestSchemaMulti,
        common_params: typing.Union[MultiSearchCommonParameters, None] = None,
    ) -> MultiSearchResponse:
        """Perform a standard multi-search operation."""

    async def perform(
        self,
        search_queries: MultiSearchRequestSchema,
        common_params: typing.Union[MultiSearchCommonParameters, None] = None,
    ) -> MultiSearchResponseSchema:
        """
        Perform a multi-search operation.

        This method allows executing multiple search queries in a single API call.
        It processes the search parameters, sends the request to the Typesense API,
        and returns the multi-search response.

        Args:
            search_queries (MultiSearchRequestSchema):
                A dictionary containing the list of search queries to perform.
                The dictionary should have a 'searches' key with a list of search
                parameter dictionaries.
            common_params (Union[MultiSearchCommonParameters, None], optional):
                Common parameters to apply to all search queries. Defaults to None.

        Returns:
            MultiSearchResponseSchema:
                A standard multi-search response for non-union requests,
                or a search response when ``union=True``.

        Example:
            >>> multi_search = AsyncMultiSearch(async_api_call)
            >>> response = await multi_search.perform(
            ...     {
            ...         "searches": [
            ...             {
            ...                 "q": "com",
            ...                 "query_by": "company_name",
            ...                 "collection": "companies",
            ...             },
            ...         ],
            ...     }
            ... )
        """
        stringified_search_params = [
            stringify_search_params(search_params)
            for search_params in search_queries.get("searches")
        ]
        search_body = {
            "searches": stringified_search_params,
            "union": search_queries.get("union", False),
        }
        entity_type: typing.Type[typing.Any]
        if search_body["union"]:
            entity_type = SearchResponse
        else:
            entity_type = MultiSearchResponse

        response: MultiSearchResponseSchema = await self.api_call.post(
            AsyncMultiSearch.resource_path,
            body=search_body,
            params=common_params,
            as_json=True,
            entity_type=entity_type,
        )
        return response
