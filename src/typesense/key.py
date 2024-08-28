from .utils import encodeURIComponent


class Key(object):
    def __init__(self, api_call, key_id):
        self.key_id = key_id
        self.api_call = api_call

    def _endpoint_path(self):
        from .keys import Keys

        return "{0}/{1}".format(Keys.RESOURCE_PATH, encodeURIComponent(self.key_id))

    def retrieve(self):
        return self.api_call.get(self._endpoint_path())

    def delete(self):
        return self.api_call.delete(self._endpoint_path())
