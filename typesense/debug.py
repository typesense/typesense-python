from api_call import ApiCall


class Debug(object):
    ENDPOINT_PATH = '/debug'

    @staticmethod
    def retrieve():
        ApiCall.get(Debug.ENDPOINT_PATH, {})
