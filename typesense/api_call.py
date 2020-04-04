import json
import time

import requests
from .exceptions import (ObjectAlreadyExists,
                         ObjectNotFound, ObjectUnprocessable,
                         RequestMalformed, RequestUnauthorized,
                         ServerError, ServiceUnavailable, TypesenseClientError)


class ApiCall(object):
    API_KEY_HEADER_NAME = 'X-TYPESENSE-API-KEY'
    CHECK_FAILED_NODE_INTERVAL_S = 60

    def __init__(self, config):
        self.config = config
        self.nodes = self.config.nodes
        self.node_index = 0
        self.last_health_check_ts = int(time.time())

    def _check_failed_node(self):
        current_epoch_ts = int(time.time())
        check_node = ((current_epoch_ts - self.last_health_check_ts) > ApiCall.CHECK_FAILED_NODE_INTERVAL_S)
        if check_node:
            self.last_health_check_ts = current_epoch_ts

        return check_node

    # Returns a healthy host from the pool in a round-robin fashion.
    # Might return an unhealthy host periodically to check for recovery.
    def get_node(self):
        i = 0
        while i < len(self.nodes):
            i += 1
            self.node_index = (self.node_index + 1) % len(self.nodes)
            if self.nodes[self.node_index].healthy or self._check_failed_node():
                return self.nodes[self.node_index]

        # None of the nodes are marked healthy, but some of them could have become healthy since last health check.
        # So we will just return the next node.
        self.node_index = (self.node_index + 1) % len(self.nodes)
        return self.nodes[self.node_index]

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
        elif http_code == 503:
            return ServiceUnavailable
        else:
            return TypesenseClientError

    # Makes the actual http request, along with retries
    def make_request(self, fn, method, endpoint, as_json, **kwargs):
        num_tries = 0
        while num_tries < self.config.num_retries:
            num_tries += 1
            node = self.get_node()
            node.healthy = False

            try:
                url = node.url() + endpoint
                if kwargs.get('data') and not isinstance(kwargs['data'], str):
                    kwargs['data'] = json.dumps(kwargs['data'])

                r = fn(url, headers={ApiCall.API_KEY_HEADER_NAME: self.config.api_key}, **kwargs)

                if 0 < r.status_code < 500:
                    node.healthy = True

                if (method != 'post' and r.status_code != 200) or \
                   (method == 'post' and not (r.status_code == 200 or r.status_code == 201)):
                    error_message = r.json().get('message', 'API error.')
                    # print('error_message: ' + error_message)
                    raise ApiCall.get_exception(r.status_code)(r.status_code, error_message)

                return r.json() if as_json else r.text
            except requests.exceptions.Timeout:
                pass
            except requests.exceptions.ConnectionError:
                pass
            except TypesenseClientError as typesense_client_error:
                raise typesense_client_error
            except Exception as e:
                raise e

            # print('Failed, retrying after sleep: ' + node.port)
            time.sleep(self.config.retry_interval_seconds)

        raise TypesenseClientError('Retries exceeded.')

    def get(self, endpoint, params=None, as_json=True):
        params = params or {}
        return self.make_request(requests.get, 'get', endpoint, as_json,
                                 params=params,
                                 timeout=self.config.timeout_seconds)

    def post(self, endpoint, body):
        return self.make_request(requests.post, 'post', endpoint, True,
                                 data=body, timeout=self.config.timeout_seconds)

    def put(self, endpoint, body):
        return self.make_request(requests.put, 'put', endpoint, True,
                                 data=body, timeout=self.config.timeout_seconds)

    def delete(self, endpoint):
        return self.make_request(requests.delete, 'delete', endpoint, True,
                                 timeout=self.config.timeout_seconds)
