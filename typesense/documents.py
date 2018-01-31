from api_call import ApiCall
from collections import Collections


class Documents(object):

    @staticmethod
    def create(collection_name, document):
        return ApiCall.post(Collections.documents_path_for(collection_name), document)

    @staticmethod
    def retrieve(collection_name, document_id):
        return ApiCall.get('{0}/{1}'.format(Collections.documents_path_for(collection_name), document_id), {})

    @staticmethod
    def delete(collection_name, document_id):
        return ApiCall.delete('{0}/{1}'.format(Collections.documents_path_for(collection_name), document_id))

    @staticmethod
    def search(collection_name, search_parameters):
        return ApiCall.get('{0}/search'.format(Collections.documents_path_for(collection_name)), search_parameters)

    @staticmethod
    def export(collection_name):
        api_response = ApiCall.get('{0}/export'.format(Collections.documents_path_for(collection_name)), {},
                                   as_json=False)
        return api_response.split('\n')
