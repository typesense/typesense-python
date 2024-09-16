"""
This module provides functionality for performing multi-search operations in the Typesense API.

It contains the MultiSearch class, which allows for executing multiple search queries
in a single API call.

Classes:
    MultiSearch: Manages multi-search operations in the Typesense API.

Dependencies:
    - typesense.api_call: Provides the ApiCall class for making API requests.
    - typesense.preprocess:
       Provides the stringify_search_params function for parameter processing.
    - typesense.types.document:
        Provides the MultiSearchCommonParameters type.
    - typesense.types.multi_search:
        Provides MultiSearchRequestSchema and MultiSearchResponse types.

Note: This module uses conditional imports to support both Python 3.11+ and earlier versions.
"""

import sys

from typesense.api_call import ApiCall
from typesense.preprocess import stringify_search_params
from typesense.types.document import MultiSearchCommonParameters
from typesense.types.multi_search import MultiSearchRequestSchema, MultiSearchResponse

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing


class MultiSearch:
    """
    Manages multi-search operations in the Typesense API.

    This class provides methods to perform multiple search queries in a single API call.

    Attributes:
        RESOURCE_PATH (str): The API endpoint path for multi-search operations.
        api_call (ApiCall): The ApiCall instance for making API requests.
    """

    resource_path: typing.Final[str] = "/multi_search"

    def __init__(self, api_call: ApiCall) -> None:
        """
        Initialize the MultiSearch instance.

        Args:
            api_call (ApiCall): The ApiCall instance for making API requests.
        """
        self.api_call = api_call

    def perform(
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
        """
        stringified_search_params = [
            stringify_search_params(search_params)
            for search_params in search_queries.get("searches")
        ]
        search_body = {"searches": stringified_search_params}
        response: MultiSearchResponse = self.api_call.post(
            MultiSearch.resource_path,
            body=search_body,
            params=common_params,
            as_json=True,
            entity_type=MultiSearchResponse,
        )
        return response
