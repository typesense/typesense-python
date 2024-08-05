from typesense.api_call import ApiCall
from typesense.types.synonym import SynonymDeleteSchema, SynonymSchema


class Synonym(object):
    def __init__(
        self, api_call: ApiCall, collection_name: str, synonym_id: str
    ) -> None:
        self.api_call = api_call
        self.collection_name = collection_name
        self.synonym_id = synonym_id

    def _endpoint_path(self) -> str:
        from .collections import Collections
        from .synonyms import Synonyms

        return "{0}/{1}/{2}/{3}".format(
            Collections.RESOURCE_PATH,
            self.collection_name,
            Synonyms.RESOURCE_PATH,
            self.synonym_id,
        )

    def retrieve(self) -> SynonymSchema:
        return self.api_call.get(self._endpoint_path(), entity_type=SynonymSchema)

    def delete(self) -> SynonymDeleteSchema:
        return self.api_call.delete(
            self._endpoint_path(), entity_type=SynonymDeleteSchema
        )
