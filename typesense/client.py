from .aliases import Aliases
from .debug import Debug
from .collections import Collections
from .keys import Keys
from .configuration import Configuration
from .api_call import ApiCall


class Client(object):
    def __init__(self, config_dict):
        self.config = Configuration(config_dict)
        self.api_call = ApiCall(self.config)
        self.collections = Collections(self.api_call)
        self.keys = Keys(self.api_call)
        self.aliases = Aliases(self.api_call)
        self.debug = Debug(self.api_call)
