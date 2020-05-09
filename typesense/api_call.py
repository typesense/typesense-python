import copy
import json
import time

import requests
from .exceptions import (ObjectAlreadyExists,
                         ObjectNotFound, ObjectUnprocessable,
                         RequestMalformed, RequestUnauthorized,
                         ServerError, ServiceUnavailable, TypesenseClientError)


class ApiCall(object):
    API_KEY_HEADER_NAME = 'X-TYPESENSE-API-KEY'

    def __init__(self, config):
        self.config = config
        self.nodes = copy.deepcopy(self.config.nodes)
        self.node_index = 0

    @staticmethod
    def check_failed_node(node, healthcheck_interval):
        current_epoch_ts = int(time.time())
        return ((current_epoch_ts - node.last_access_ts) > healthcheck_interval)

    # Returns a healthy host from the pool in a round-robin fashion.
    # Might return an unhealthy host periodically to check for recovery.
    def get_node(self):
        i = 0
        while i < len(self.nodes):
            i += 1
            node = self.nodes[self.node_index]
            self.node_index = (self.node_index + 1) % len(self.nodes)
            healthcheck_interval = self.config.healthcheck_interval_seconds

            if node.healthy or ApiCall.check_failed_node(node, healthcheck_interval):
                return node

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
    def make_request(self, fn, endpoint, as_json, **kwargs):
        num_tries = 0
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
                    # print('error_message: ' + error_message)
                    raise ApiCall.get_exception(r.status_code)(r.status_code, error_message)

                return r.json() if as_json else r.text
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.HTTPError,
                    requests.exceptions.RequestException, requests.exceptions.SSLError):
                # Catch the exception and retry
                pass

            # print('Failed, retrying after sleep: ' + node.port)
            time.sleep(self.config.retry_interval_seconds)

        raise TypesenseClientError('Retries exceeded.')

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
