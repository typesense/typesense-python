from api_call import ApiCall


class Collections(object):
    ENDPOINT_PATH = '/collections'

    @staticmethod
    def create(schema):
        return ApiCall.post(Collections.ENDPOINT_PATH, schema)

    @staticmethod
    def retrieve(collection_name):
        return ApiCall.get('{0}/{1}'.format(Collections.ENDPOINT_PATH, collection_name), {})

    @staticmethod
    def delete(collection_name):
        return ApiCall.delete('{0}/{1}'.format(Collections.ENDPOINT_PATH, collection_name))

    @staticmethod
    def retrieve_all():
        return ApiCall.get('{0}'.format(Collections.ENDPOINT_PATH), {})

    @staticmethod
    def documents_path_for(collection_name):
        return '{0}/{1}/documents'.format(Collections.ENDPOINT_PATH, collection_name)
