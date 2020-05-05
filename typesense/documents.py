import json

from .document import Document


class Documents(object):
    RESOURCE_PATH = 'documents'

    def __init__(self, config, api_call, collection_name):
        self.config = config
        self.api_call = api_call
        self.collection_name = collection_name
        self.documents = {}

    def __getitem__(self, document_id):
        if document_id not in self.documents:
            self.documents[document_id] = Document(self.config, self.api_call, self.collection_name, document_id)

        return self.documents[document_id]

    def _endpoint_path(self, action=None):
        from .collections import Collections

        action = action or ''
        return u"{0}/{1}/{2}/{3}".format(Collections.RESOURCE_PATH, self.collection_name, Documents.RESOURCE_PATH,
                                         action)

    def create(self, document):
        return self.api_call.post(self._endpoint_path(), document)

    def create_many(self, documents):
        document_strs = []
        for document in documents:
            document_strs.append(json.dumps(document))

        docs_import = '\n'.join(document_strs)
        return self.api_call.post(self._endpoint_path('import'), docs_import)

    def export(self):
        api_response = self.api_call.get(self._endpoint_path('export'), {}, as_json=False)
        return api_response.split('\n')

    def search(self, search_parameters):
        return self.api_call.get(self._endpoint_path('search'), search_parameters)
