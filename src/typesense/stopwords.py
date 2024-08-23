import sys

from typesense.api_call import ApiCall
from typesense.types.stopword import (
    StopwordCreateSchema,
    StopwordSchema,
    StopwordsRetrieveSchema,
)

from .stopwords_set import StopwordsSet

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing


class Stopwords(object):
    RESOURCE_PATH = "/stopwords"

    def __init__(self, api_call: ApiCall):
        self.api_call = api_call
        self.stopwords_sets: typing.Dict[str, StopwordsSet] = {}

    def __getitem__(self, stopwords_set_id: str) -> StopwordsSet:
        if not self.stopwords_sets.get(stopwords_set_id):
            self.stopwords_sets[stopwords_set_id] = StopwordsSet(
                self.api_call, stopwords_set_id
            )
        return self.stopwords_sets[stopwords_set_id]

    def upsert(
        self, stopwords_set_id: str, stopwords_set: StopwordCreateSchema
    ) -> StopwordSchema:
        response: StopwordSchema = self.api_call.put(
            "{}/{}".format(Stopwords.RESOURCE_PATH, stopwords_set_id),
            body=stopwords_set,
            entity_type=StopwordSchema,
        )
        return response

    def retrieve(self) -> StopwordsRetrieveSchema:
        response: StopwordsRetrieveSchema = self.api_call.get(
            "{0}".format(Stopwords.RESOURCE_PATH),
            as_json=True,
            entity_type=StopwordsRetrieveSchema,
        )
        return response
