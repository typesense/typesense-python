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
    def validate_configuration():
        if not master_node.initialized():
            raise ConfigError('Bad master node configuration.')

        for read_replica_node in read_replica_nodes:
            if not read_replica_node.initialized():
                raise ConfigError('Bad read replica node configuration.')

    @staticmethod
    def get(endpoint):
        ApiCall.validate_configuration()

        typesense_nodes = ApiCall.nodes()
        for node in typesense_nodes:
            url = node.url() + endpoint
            try:
                r = requests.get(url, headers={API_KEY_HEADER_NAME: node.api_key}, timeout=timeout_seconds)
                if r.status_code != 200:
                    error_message = r.json().get('message', '')
                    raise ApiCall.get_exception(r.status_code)(error_message)
                return r.json()
            except requests.exceptions.Timeout:
                pass
            except requests.exceptions.ConnectionError:
                pass
            except TypesenseClientError as typesense_client_error:
                raise typesense_client_error
            except Exception as e:
                raise e

        raise TypesenseClientError('All hosts are bad.')

    @staticmethod
    def post(endpoint, body):
        ApiCall.validate_configuration()

        typesense_nodes = ApiCall.nodes()
        for node in typesense_nodes:
            url = node.url() + endpoint
            try:
                r = requests.post(url, json=body, headers={API_KEY_HEADER_NAME: node.api_key},
                                  timeout=timeout_seconds)
                if r.status_code != 201:
                    error_message = r.json().get('message', '')
                    raise ApiCall.get_exception(r.status_code)(error_message)
                return r.json()
            except requests.exceptions.Timeout:
                pass
            except requests.exceptions.ConnectionError:
                pass
            except TypesenseClientError as typesense_client_error:
                raise typesense_client_error
            except Exception as e:
                raise e

        raise TypesenseClientError('All hosts are bad.')
