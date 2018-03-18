from .documents import Documents
from .api_call import ApiCall


class Collection(object):
    def __init__(self, config, name):
        self.config = config
        self.name = name
        self.api_call = ApiCall(config)
        self.documents = Documents(config, name)

    def _endpoint_path(self):
        from .collections import Collections
        return u"{0}/{1}".format(Collections.RESOURCE_PATH, self.name)

    def retrieve(self):
        return self.api_call.get(self._endpoint_path())

    def delete(self):
        return self.api_call.delete(self._endpoint_path())
