from .collections import Collections
from .configuration import Configuration


class Client(object):
    def __init__(self, config_dict):
        self.config = Configuration(config_dict)
        self.collections = Collections(self.config)
