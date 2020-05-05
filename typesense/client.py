from .aliases import Aliases
from .debug import Debug
from .collections import Collections
from .configuration import Configuration
from .api_call import ApiCall


class Client(object):
    def __init__(self, config_dict):
        self.config = Configuration(config_dict)
        self.api_call = ApiCall(self.config)
        self.collections = Collections(self.config, self.api_call)
        self.aliases = Aliases(self.config, self.api_call)
        self.debug = Debug(self.config, self.api_call)
