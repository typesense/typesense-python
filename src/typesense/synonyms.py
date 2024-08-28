from .synonym import Synonym
from .utils import encodeURIComponent


class Synonyms(object):
    RESOURCE_PATH = "synonyms"

    def __init__(self, api_call, collection_name):
        self.api_call = api_call
        self.collection_name = collection_name
        self.synonyms = {}

    def __getitem__(self, synonym_id):
        if synonym_id not in self.synonyms:
            self.synonyms[synonym_id] = Synonym(
                self.api_call, self.collection_name, synonym_id
            )

        return self.synonyms[synonym_id]

    def _endpoint_path(self, synonym_id=None):
        from .collections import Collections

        synonym_id = synonym_id or ""
        return "{0}/{1}/{2}/{3}".format(
            Collections.RESOURCE_PATH,
            encodeURIComponent(self.collection_name),
            Synonyms.RESOURCE_PATH,
            encodeURIComponent(synonym_id),
        )

    def upsert(self, id, schema):
        return self.api_call.put(self._endpoint_path(id), schema)

    def retrieve(self):
        return self.api_call.get(self._endpoint_path())
