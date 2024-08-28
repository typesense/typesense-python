import sys

from typesense.api_call import ApiCall
from typesense.preprocess import stringify_search_params
from typesense.types.document import MultiSearchCommonParameters
from typesense.types.multi_search import MultiSearchRequestSchema, MultiSearchResponse

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing


class MultiSearch(object):
    RESOURCE_PATH = "/multi_search"

    def __init__(self, api_call: ApiCall) -> None:
        self.api_call = api_call

    def perform(
        self,
        search_queries: MultiSearchRequestSchema,
        common_params: typing.Union[MultiSearchCommonParameters, None] = None,
    ) -> MultiSearchResponse:
        stringified_search_params = [
            stringify_search_params(search_params)
            for search_params in search_queries.get("searches")
        ]
        search_body = {"searches": stringified_search_params}
        response: MultiSearchResponse = self.api_call.post(
            MultiSearch.RESOURCE_PATH,
            body=search_body,
            params=common_params,
            as_json=True,
            entity_type=MultiSearchResponse,
        )
        return response
