import sys

from typesense.api_call import ApiCall
from typesense.types.synonym import (
    SynonymCreateSchema,
    SynonymSchema,
    SynonymsRetrieveSchema,
)

from .synonym import Synonym

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing


class Synonyms(object):
    RESOURCE_PATH = 'synonyms'

    def __init__(self, api_call: ApiCall, collection_name: str):
        self.api_call = api_call
        self.collection_name = collection_name
        self.synonyms: typing.Dict[str, Synonym] = {}

    def __getitem__(self, synonym_id: str) -> Synonym:
        if not self.synonyms.get(synonym_id):
            self.synonyms[synonym_id] = Synonym(
                self.api_call, self.collection_name, synonym_id
            )

        return self.synonyms[synonym_id]

    def _endpoint_path(self, synonym_id: typing.Union[str, None] = None) -> str:
        from typesense.collections import Collections

        synonym_id = synonym_id or ""
        return "{0}/{1}/{2}/{3}".format(
            Collections.RESOURCE_PATH,
            self.collection_name,
            Synonyms.RESOURCE_PATH,
            synonym_id,
        )

    def upsert(self, id: str, schema: SynonymCreateSchema) -> SynonymSchema:
        response = self.api_call.put(
            self._endpoint_path(id), body=schema, entity_type=SynonymSchema
        )

        return response

    def retrieve(self) -> SynonymsRetrieveSchema:
        response = self.api_call.get(
            self._endpoint_path(), entity_type=SynonymsRetrieveSchema
        )
        return response
