from .overrides import Overrides
from .documents import Documents


class Collection(object):
    def __init__(self, config, api_call, name):
        self.config = config
        self.name = name
        self.api_call = api_call
        self.documents = Documents(config, api_call, name)
        self.overrides = Overrides(config, api_call, name)

    def _endpoint_path(self):
        from .collections import Collections
        return u"{0}/{1}".format(Collections.RESOURCE_PATH, self.name)

    def retrieve(self):
        return self.api_call.get(self._endpoint_path())

    def delete(self):
        return self.api_call.delete(self._endpoint_path())