from .api_call import ApiCall
from .collection import Collection


class Collections(object):
    RESOURCE_PATH = '/collections'

    def __init__(self, config):
        self.config = config
        self.api_call = ApiCall(config)
        self.collections = {}

    def __getitem__(self, collection_name):
        if collection_name not in self.collections:
            self.collections[collection_name] = Collection(self.config, collection_name)

        return self.collections.get(collection_name)

    def create(self, schema):
        return self.api_call.post(Collections.RESOURCE_PATH, schema)

    def retrieve(self):
        return self.api_call.get('{0}'.format(Collections.RESOURCE_PATH))
