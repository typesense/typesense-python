from api_call import ApiCall


class Collections(object):
    ENDPOINT_PATH = '/collections'

    @staticmethod
    def create(schema):
        return ApiCall.post(Collections.ENDPOINT_PATH, schema)

    @staticmethod
    def retrieve(collection_name):
        return ApiCall.get("{0}/{1}".format(Collections.ENDPOINT_PATH, collection_name))