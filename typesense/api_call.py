import requests

from .exceptions import (ObjectAlreadyExists,
                         ObjectNotFound, ObjectUnprocessable,
                         RequestMalformed, RequestUnauthorized,
                         ServerError, TypesenseClientError)


class ApiCall(object):
    API_KEY_HEADER_NAME = 'X-TYPESENSE-API-KEY'

    def __init__(self, config):
        self.config = config

    def nodes(self):
        return [self.config.master_node] + self.config.read_replica_nodes

    @staticmethod
    def get_exception(http_code):
        if http_code == 400:
            return RequestMalformed
        elif http_code == 401:
            return RequestUnauthorized
        elif http_code == 404:
            return ObjectNotFound
        elif http_code == 409:
            return ObjectAlreadyExists
        elif http_code == 422:
            return ObjectUnprocessable
        elif http_code == 500:
            return ServerError
        else:
            return TypesenseClientError

    def get(self, endpoint, params=None, as_json=True):
        params = params or {}

        for node in self.nodes():
            url = node.url() + endpoint
            try:
                r = requests.get(url,
                                 headers={ApiCall.API_KEY_HEADER_NAME: node.api_key},
                                 params=params,
                                 timeout=self.config.timeout_seconds)
                if r.status_code != 200:
                    error_message = r.json().get('message', 'API error.')
                    raise ApiCall.get_exception(r.status_code)(error_message)
                return r.json() if as_json else r.text
            except requests.exceptions.Timeout:
                pass
            except requests.exceptions.ConnectionError:
                pass
            except TypesenseClientError as typesense_client_error:
                raise typesense_client_error
            except Exception as e:
                raise e

        raise TypesenseClientError('All hosts are bad.')

    def post(self, endpoint, body):
        url = self.config.master_node.url() + endpoint
        api_key = self.config.master_node.api_key

        r = requests.post(url, json=body,
                          headers={ApiCall.API_KEY_HEADER_NAME: api_key},
                          timeout=self.config.timeout_seconds)
        if r.status_code != 201:
            error_message = r.json().get('message', 'API error.')
            print(url)
            raise ApiCall.get_exception(r.status_code)(error_message)

        return r.json()

    def delete(self, endpoint):
        url = self.config.master_node.url() + endpoint
        api_key = self.config.master_node.api_key

        r = requests.delete(url,
                            headers={ApiCall.API_KEY_HEADER_NAME: api_key},
                            timeout=self.config.timeout_seconds)
        if r.status_code != 200:
            error_message = r.json().get('message', 'API error.')
            raise ApiCall.get_exception(r.status_code)(error_message)

        return r.json()
