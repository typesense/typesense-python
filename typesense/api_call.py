import requests
from . import *
from exceptions import *

API_KEY_HEADER_NAME = 'X-TYPESENSE-API-KEY'


class ApiCall(object):
    @staticmethod
    def nodes():
        return [master_node] + read_replica_nodes

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

    @staticmethod
    def get(endpoint):
        typesense_nodes = ApiCall.nodes()

        for node in typesense_nodes:
            url = node.url() + endpoint
            try:
                r = requests.get(url, headers={API_KEY_HEADER_NAME: node.api_key}, timeout=timeout_seconds)
                if r.status_code != 200:
                    raise ApiCall.get_exception(r.status_code)()
                return r.json()
            except TypesenseClientError as typesense_client_error:
                raise typesense_client_error
            except requests.exceptions.Timeout:
                pass
            except requests.exceptions.ConnectionError:
                pass
            except Exception as e:
                raise e

        raise Exception("All hosts are bad.")

    @staticmethod
    def post(endpoint, body):
        # TODO: validate config!

        typesense_nodes = ApiCall.nodes()
        for node in typesense_nodes:
            url = node.url() + endpoint
            try:
                r = requests.post(url, json=body, headers={API_KEY_HEADER_NAME: node.api_key},
                                  timeout=timeout_seconds)
                if r.status_code != 201:
                    print r.text
                    raise ApiCall.get_exception(r.status_code)()
                return r.json()
            except TypesenseClientError as typesense_client_error:
                raise typesense_client_error
            except requests.exceptions.Timeout:
                pass
            except requests.exceptions.ConnectionError:
                pass
            except Exception as e:
                raise e

        raise Exception("All hosts are bad.")
