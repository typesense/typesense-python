from .override import Override
from .api_call import ApiCall


class Overrides(object):
    RESOURCE_PATH = 'overrides'

    def __init__(self, config, collection_name):
        self.config = config
        self.api_call = ApiCall(config)
        self.collection_name = collection_name
        self.overrides = {}

    def __getitem__(self, override_id):
        if override_id not in self.overrides:
            self.overrides[override_id] = Override(self.config, self.collection_name, override_id)

        return self.overrides[override_id]

    def _endpoint_path(self, override_id=None):
        from .collections import Collections
        override_id = override_id or ''
        return u"{0}/{1}/{2}/{3}".format(Collections.RESOURCE_PATH, self.collection_name,
                                         Overrides.RESOURCE_PATH, override_id)

    def upsert(self, id, config):
        return self.api_call.put(self._endpoint_path(id), config)

    def retrieve(self):
        return self.api_call.get(self._endpoint_path())
