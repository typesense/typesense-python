from typesense.alias import Alias
from .api_call import ApiCall


class Aliases(object):
    RESOURCE_PATH = '/aliases'

    def __init__(self, config):
        self.config = config
        self.api_call = ApiCall(config)
        self.aliases = {}

    def __getitem__(self, name):
        if name not in self.aliases:
            self.aliases[name] = Alias(self.config, name)

        return self.aliases.get(name)

    def _endpoint_path(self, alias_name):
        return u"{0}/{1}".format(Aliases.RESOURCE_PATH, alias_name)

    def upsert(self, name, mapping):
        return self.api_call.put(self._endpoint_path(name), mapping)

    def retrieve(self):
        return self.api_call.get(Aliases.RESOURCE_PATH)
