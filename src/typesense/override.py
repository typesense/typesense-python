from .utils import encodeURIComponent


class Override(object):
    def __init__(self, api_call, collection_name, override_id):
        self.api_call = api_call
        self.collection_name = collection_name
        self.override_id = override_id

    def _endpoint_path(self):
        from .collections import Collections
        from .overrides import Overrides

        return "{0}/{1}/{2}/{3}".format(
            Collections.RESOURCE_PATH,
            encodeURIComponent(self.collection_name),
            Overrides.RESOURCE_PATH,
            encodeURIComponent(self.override_id),
        )

    def retrieve(self):
        return self.api_call.get(self._endpoint_path())

    def delete(self):
        return self.api_call.delete(self._endpoint_path())
