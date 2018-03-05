from collections import Collections

from api_call import ApiCall


class Documents(object):
    @staticmethod
    def create(coll_name, document):
        return ApiCall.post(Collections.documents_path_for(coll_name),
                            document)

    @staticmethod
    def retrieve(coll_name, document_id):
        return ApiCall.get('{0}/{1}'.format(Collections.documents_path_for(coll_name), document_id), {})

    @staticmethod
    def delete(coll_name, document_id):
        return ApiCall.delete('{0}/{1}'.format(Collections.documents_path_for(coll_name), document_id))

    @staticmethod
    def search(coll_name, search_parameters):
        return ApiCall.get('{0}/search'.format(Collections.documents_path_for(coll_name)), search_parameters)

    @staticmethod
    def export(coll_name):
        api_response = ApiCall.get('{0}/export'.format(Collections.documents_path_for(coll_name)), {}, as_json=False)
        return api_response.split('\n')
