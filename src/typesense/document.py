from .utils import encodeURIComponent


class Document(object):
    def __init__(self, api_call, collection_name, document_id):
        self.api_call = api_call
        self.collection_name = collection_name
        self.document_id = document_id

    def _endpoint_path(self):
        from .collections import Collections
        from .documents import Documents

        return "{0}/{1}/{2}/{3}".format(
            Collections.RESOURCE_PATH,
            encodeURIComponent(self.collection_name),
            Documents.RESOURCE_PATH,
            encodeURIComponent(self.document_id),
        )

    def retrieve(self):
        return self.api_call.get(self._endpoint_path())

    def update(self, document, params=None):
        return self.api_call.patch(self._endpoint_path(), document, params)

    def delete(self):
        return self.api_call.delete(self._endpoint_path())
