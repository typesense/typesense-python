import copy
import json
import time

import requests
from .exceptions import (HTTPStatus0Error, ObjectAlreadyExists,
                         ObjectNotFound, ObjectUnprocessable,
                         RequestMalformed, RequestUnauthorized,
                         ServerError, ServiceUnavailable, TypesenseClientError)


class ApiCall(object):
    API_KEY_HEADER_NAME = 'X-TYPESENSE-API-KEY'

    def __init__(self, config):
        self.config = config
        self.nodes = copy.deepcopy(self.config.nodes)
        self.node_index = 0

    def check_failed_node(self, node):
        current_epoch_ts = int(time.time())
        return (current_epoch_ts - node.last_access_ts) > self.config.healthcheck_interval_seconds

    # Returns a healthy host from the pool in a round-robin fashion.
    # Might return an unhealthy host periodically to check for recovery.
    def get_node(self):
        i = 0
        while i < len(self.nodes):
            i += 1
            node = self.nodes[self.node_index]
            self.node_index = (self.node_index + 1) % len(self.nodes)

            if node.healthy or self.check_failed_node(node):
                return node

        # None of the nodes are marked healthy, but some of them could have become healthy since last health check.
        # So we will just return the next node.
        return self.nodes[self.node_index]

    @staticmethod
    def get_exception(http_code):
        if http_code == 0:
            return HTTPStatus0Error
        elif http_code == 400:
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
    def make_request(self, fn, endpoint, as_json, **kwargs):
        num_tries = 0
        last_exception = None

        while num_tries < (self.config.num_retries + 1):
            num_tries += 1
            node = self.get_node()

            # We assume node to be unhealthy, unless proven healthy.
            # This way, we keep things DRY and don't have to repeat setting healthy as false multiple times.
            node.healthy = False
            node.last_access_ts = int(time.time())

            try:
                url = node.url() + endpoint
                if kwargs.get('data') and not isinstance(kwargs['data'], str):
                    kwargs['data'] = json.dumps(kwargs['data'])

                r = fn(url, headers={ApiCall.API_KEY_HEADER_NAME: self.config.api_key}, **kwargs)

                # Treat any status code > 0 and < 500 to be an indication that node is healthy
                # We exclude 0 since some clients return 0 when request fails
                if 0 < r.status_code < 500:
                    node.healthy = True

                # We should raise a custom exception if status code is not 200 or 201
                if r.status_code not in [200, 201]:
                    error_message = r.json().get('message', 'API error.')
                    # Raised exception will be caught and retried only if it's a 50X
                    raise ApiCall.get_exception(r.status_code)(r.status_code, error_message)

                return r.json() if as_json else r.text
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.HTTPError,
                    requests.exceptions.RequestException, requests.exceptions.SSLError,
                    HTTPStatus0Error, ServerError, ServiceUnavailable) as e:
                # Catch the exception and retry
                last_exception = e
                time.sleep(self.config.retry_interval_seconds)

        raise last_exception

    def get(self, endpoint, params=None, as_json=True):
        params = params or {}
        return self.make_request(requests.get, endpoint, as_json,
                                 params=params,
                                 timeout=self.config.timeout_seconds)

    def post(self, endpoint, body):
        return self.make_request(requests.post, endpoint, True,
                                 data=body, timeout=self.config.timeout_seconds)

    def put(self, endpoint, body):
        return self.make_request(requests.put, endpoint, True,
                                 data=body, timeout=self.config.timeout_seconds)

    def delete(self, endpoint):
        return self.make_request(requests.delete, endpoint, True,
                                 timeout=self.config.timeout_seconds)
