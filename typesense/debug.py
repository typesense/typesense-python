class Debug(object):
    RESOURCE_PATH = '/debug'

    def __init__(self, config, api_call):
        self.config = config
        self.api_call = api_call
        self.collections = {}

    def retrieve(self):
        return self.api_call.get('{0}'.format(Debug.RESOURCE_PATH))
