from typesense.api_call import ApiCall
from typesense.types.stopword import StopwordDeleteSchema, StopwordsSingleRetrieveSchema


class StopwordsSet:
    def __init__(self, api_call: ApiCall, stopwords_set_id: str) -> None:
        self.stopwords_set_id = stopwords_set_id
        self.api_call = api_call

    @property
    def _endpoint_path(self) -> str:
        from .stopwords import Stopwords

        return "{0}/{1}".format(Stopwords.RESOURCE_PATH, self.stopwords_set_id)

    def retrieve(self) -> StopwordsSingleRetrieveSchema:
        response: StopwordsSingleRetrieveSchema = self.api_call.get(
            self._endpoint_path, as_json=True, entity_type=StopwordsSingleRetrieveSchema
        )
        return response

    def delete(self) -> StopwordDeleteSchema:
        response: StopwordDeleteSchema = self.api_call.delete(
            self._endpoint_path, entity_type=StopwordDeleteSchema
        )
        return response
