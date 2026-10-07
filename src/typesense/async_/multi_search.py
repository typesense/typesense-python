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
from .stream import (
    AsyncSearchStream,
    consume_stream,
    notify_error,
    resolve_stream_config,
)
from typesense.preprocess import stringify_search_params
from typesense.types.document import MultiSearchCommonParameters
from typesense.types.multi_search import MultiSearchRequestSchema, MultiSearchResponse

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

    async def perform(
        self,
        search_queries: MultiSearchRequestSchema,
        common_params: typing.Union[MultiSearchCommonParameters, None] = None,
    ) -> MultiSearchResponse:
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
            MultiSearchResponse:
                The response from the multi-search operation, containing
                the results of all search queries.

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

        With ``conversation_stream`` enabled in ``common_params``, the LLM's answer
        is streamed and the callbacks in ``stream_config`` run as it arrives. To
        iterate over the answer instead, use ``perform_stream``.
        """
        if common_params and common_params.get("conversation_stream"):
            stream_config = resolve_stream_config(common_params.get("stream_config"))
            try:
                search_stream = await self.perform_stream(search_queries, common_params)
                streamed_response: MultiSearchResponse = await consume_stream(
                    search_stream,
                    stream_config,
                )
            except Exception as error:
                notify_error(stream_config, error)
                raise
            return streamed_response

        response: MultiSearchResponse = await self.api_call.post(
            AsyncMultiSearch.resource_path,
            body=self._search_body(search_queries),
            params=_without_stream_config(common_params) if common_params else None,
            as_json=True,
            entity_type=MultiSearchResponse,
        )
        return response

    async def perform_stream(
        self,
        search_queries: MultiSearchRequestSchema,
        common_params: typing.Union[MultiSearchCommonParameters, None] = None,
    ) -> AsyncSearchStream[MultiSearchResponse]:
        """
        Perform a multi-search, streaming the LLM's answer as it is generated.

        The searches' hits are combined into one context for a single answer, sent
        in the response's top-level ``conversation``. Iterate over the returned
        stream for the pieces of the answer, then call its ``get_final_response``
        for the multi-search response. Use the stream as a context manager so the
        connection is released if you stop early.

        ``conversation`` and ``conversation_stream`` are enabled for you; pass
        ``q`` and the ``conversation_model_id`` in ``common_params``, since
        Typesense reads them from the query string. ``stream_config`` is ignored.

        Args:
            search_queries (MultiSearchRequestSchema): The searches to perform.
            common_params (Union[MultiSearchCommonParameters, None], optional):
                Parameters for every search, including the conversation parameters.

        Returns:
            AsyncSearchStream[MultiSearchResponse]: The open stream.
        """
        stream_params: typing.Dict[str, object] = {
            "conversation": True,
            **_without_stream_config(common_params or {}),
            "conversation_stream": True,
        }
        return await self.api_call.stream(
            "POST",
            AsyncMultiSearch.resource_path,
            entity_type=MultiSearchResponse,
            params=stream_params,
            body=self._search_body(search_queries),
        )

    @staticmethod
    def _search_body(
        search_queries: MultiSearchRequestSchema,
    ) -> typing.Dict[str, object]:
        """Build the request body, with every search's parameters stringified."""
        stringified_search_params = [
            stringify_search_params(search_params)
            for search_params in search_queries.get("searches")
        ]
        return {
            "searches": stringified_search_params,
            "union": search_queries.get("union", False),
        }


def _without_stream_config(
    common_params: MultiSearchCommonParameters,
) -> typing.Dict[str, object]:
    """Return the parameters to send, leaving out the client-side ``stream_config``."""
    return {
        param: param_value
        for param, param_value in common_params.items()
        if param != "stream_config"
    }
