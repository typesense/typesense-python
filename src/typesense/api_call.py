"""
This module is responsible for making HTTP requests to the Typesense API.

Classes:
    - ApiCall: A class that makes HTTP requests to the Typesense API.

Functions:
    - get_exception: Get the exception class for a given HTTP status code.
    - normalize_params: Normalize boolean values in the request parameters to strings.
    - make_request: Make the actual HTTP request, along with retries.
    - node_due_for_health_check: Check if a node is due for a health check.
    - set_node_healthcheck: Set the health status of a node and update the 
        last access timestamp.
    - get_node: Get a healthy host from the pool in a round-robin fashion.
    - initialize_nodes: Initialize the nodes in the pool.
    - get: Make a GET request to the endpoint with the given parameters.
    - post: Make a POST request to the endpoint with the given parameters.
    - put: Make a PUT request to the endpoint with the given parameters.
    - patch: Make a PATCH request to the endpoint with the given parameters.
    - delete: Make a DELETE request to the endpoint with the given parameters.

Exceptions:
    - HTTPStatus0Error: An exception raised when the status code is 0.
    - RequestMalformed: An exception raised when the status code is 400.
    - RequestUnauthorized: An exception raised when the status code is 401.
    - RequestForbidden: An exception raised when the status code is 403.
    - ObjectNotFound: An exception raised when the status code is 404.
    - ObjectAlreadyExists: An exception raised when the status code is 409.
    - ObjectUnprocessable: An exception raised when the status code is 422.
    - ServerError: An exception raised when the status code is 500.
    - ServiceUnavailable: An exception raised when the status code is 503.
    - TypesenseClientError: An exception raised when the status code is not one of the above.
"""

from __future__ import annotations

import copy
import json
import sys
import time

import requests
from typesense.configuration import Configuration, Node
from .logger import logger
session = requests.session()

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

import typesense.exceptions as exceptions
TParams = typing.TypeVar("TParams", bound=typing.Dict[str, typing.Any])
TBody = typing.TypeVar("TBody", bound=typing.Dict[str, typing.Any])
TEntityDict = typing.TypeVar("TEntityDict")
class SessionFunctionKwargs(typing.Generic[TParams, TBody], typing.TypedDict):
    """
    Dictionary of keyword arguments for the session function.

    Attributes:
        params (TParams | None): The request parameters.
        data (TBody | str): The request body.
        timeout (float): The timeout for the request.
        verify (bool): Whether to verify
    """

    params: typing.NotRequired[TParams | None]
    data: typing.NotRequired[TBody | str]
    timeout: float
    verify: bool


    API_KEY_HEADER_NAME = 'X-TYPESENSE-API-KEY'
class ApiCall(typing.Generic[TEntityDict, TParams, TBody]):
    """Handles API calls to Typesense with retry and node selection logic.

    This class manages API requests to Typesense, including node selection,
    health checks, retries, and error handling. It supports various HTTP methods
    and handles authentication and request formatting.

    Attributes:
        API_KEY_HEADER_NAME (str): The header name for the API key.
        config (Configuration): The configuration for the API client.
        nodes (List[Node]): A copy of the nodes from the configuration.
        node_index (int): The current index for round-robin node selection.

    Methods:
        get_node: Selects a healthy node for the next API call.
        make_request: Executes an API request with retries and error handling.
        get: Performs a GET request.
        post: Performs a POST request.
        put: Performs a PUT request.
        patch: Performs a PATCH request.
        delete: Performs a DELETE request.
    """

    def __init__(self, config: Configuration):
        """Initializes the ApiCall instance with the given configuration.

        Args:
            config (Configuration): The configuration for the API client.
        """
        self.config = config
        self.nodes = copy.deepcopy(self.config.nodes)
        self.node_index = 0
        self._initialize_nodes()

    def _initialize_nodes(self) -> None:
        if self.config.nearest_node:
            self.set_node_healthcheck(self.config.nearest_node, True)

        for node in self.nodes:
            self.set_node_healthcheck(node, True)

    def node_due_for_health_check(self, node: Node) -> bool:
        current_epoch_ts = int(time.time())
        due_for_check: bool = (current_epoch_ts - node.last_access_ts) > self.config.healthcheck_interval_seconds
        if due_for_check:
            logger.debug('Node {}:{} is due for health check.'.format(node.host, node.port))
        return due_for_check

    # Returns a healthy host from the pool in a round-robin fashion.
    # Might return an unhealthy host periodically to check for recovery.
    def get_node(self) -> Node:
        """
        Return a healthy host from the pool in a round-robin fashion.

        Might return an unhealthy host periodically to check for recovery.

        Returns:
            Node: The healthy host from the pool in a round-robin fashion.
        """
        if self.config.nearest_node:
            if self.config.nearest_node.healthy or self.node_due_for_health_check(self.config.nearest_node):
                logger.debug('Using nearest node.')
                return self.config.nearest_node
            else:
                logger.debug('Nearest node is unhealthy or not due for health check. Falling back to individual nodes.')

        i = 0
        while i < len(self.nodes):
            i += 1
            node = self.nodes[self.node_index]
            self.node_index = (self.node_index + 1) % len(self.nodes)

            if node.healthy or self.node_due_for_health_check(node):
                return node

        # None of the nodes are marked healthy, but some of them could have become healthy since last health check.
        # So we will just return the next node.
        logger.debug('No healthy nodes were found. Returning the next node.')
        return self.nodes[self.node_index]

    @staticmethod
    def get_exception(http_code: int) -> type[exceptions.TypesenseClientError]:
        """
        Return the exception class for a given HTTP status code.

        Args:
            http_code (int): The HTTP status code.

        Returns:
            Type[TypesenseClientError]: The exception class for the given HTTP status code.
        """
        if http_code == 0:
            return exceptions.HTTPStatus0Error
        elif http_code == 400:
            return exceptions.RequestMalformed
        elif http_code == 401:
            return exceptions.RequestUnauthorized
        elif http_code == 403:
            return exceptions.RequestForbidden
        elif http_code == 404:
            return exceptions.ObjectNotFound
        elif http_code == 409:
            return exceptions.ObjectAlreadyExists
        elif http_code == 422:
            return exceptions.ObjectUnprocessable
        elif http_code == 500:
            return exceptions.ServerError
        elif http_code == 503:
            return exceptions.ServiceUnavailable
        else:
            return exceptions.TypesenseClientError

    @typing.overload
    def make_request(
        self,
        fn: typing.Callable[..., requests.models.Response],
        endpoint: str,
        as_json: typing.Literal[True],
        **kwargs: typing.Unpack[SessionFunctionKwargs[TParams, TBody]],
    ) -> TEntityDict:
        """
        Use a session function to make a request to the endpoint with the given kwargs.

        Args:
            fn (Callable[..., requests.models.Response]): The session function to use.
            endpoint (str): The endpoint to make the request to.
            as_json (bool): Whether to return the response as a JSON object.
            kwargs (SessionFunctionKwargs): The keyword arguments for the session function.

        Returns:
            TEntityDict: The response from the request in json format.

        :raises:
            HTTPStatus0Error: If the status code is 0.

            RequestMalformed: If the status code is 400.

            RequestUnauthorized: If the status code is 401.

            RequestForbidden: If the status code is 403.

            ObjectNotFound: If the status code is 404.

            ObjectAlreadyExists: If the status code is 409.

            ObjectUnprocessable: If the status code is 422.

            ServerError: If the status code is 500.

            ServiceUnavailable: If the status code is 503.

            TypesenseClientError: If the status code is not one of the above.
        """

    @typing.overload
    def make_request(
        self,
        fn: typing.Callable[..., requests.models.Response],
        endpoint: str,
        as_json: typing.Literal[False],
        **kwargs: typing.Unpack[SessionFunctionKwargs[TParams, TBody]],
    ) -> str:
        """
        Use a session function to make a request to the endpoint with the given kwargs.

        Args:
            fn (Callable[..., requests.models.Response]): The session function to use.
            endpoint (str): The endpoint to make the request to.
            as_json (bool): Whether to return the response as a JSON object.
            kwargs (SessionFunctionKwargs): The keyword arguments for the session function.

        Returns:
            str: The response from the request in text format.

        :raises:
            HTTPStatus0Error: If the status code is 0.

            RequestMalformed: If the status code is 400.

            RequestUnauthorized: If the status code is 401.

            RequestForbidden: If the status code is 403.

            ObjectNotFound: If the status code is 404.

            ObjectAlreadyExists: If the status code is 409.

            ObjectUnprocessable: If the status code is 422.

            ServerError: If the status code is 500.

            ServiceUnavailable: If the status code is 503.

            TypesenseClientError: If the status code is not one of the above.
        """

    # Makes the actual http request, along with retries
    def make_request(
        self,
        fn: typing.Callable[..., requests.models.Response],
        endpoint: str,
        as_json: bool,
        **kwargs: typing.Unpack[SessionFunctionKwargs[TParams, TBody]],
    ) -> TEntityDict | str:
        """
        Use a session function to make a request to the endpoint with the given kwargs.

        Args:
            fn (Callable[..., requests.models.Response]): The session function to use.
            endpoint (str): The endpoint to make the request to.
            as_json (bool): Whether to return the response as a JSON object.
            kwargs (SessionFunctionKwargs): The keyword arguments for the session function.

        Returns:
            Union[TEntityDict, str]: The response from the request.

        :raises:
            HTTPStatus0Error: If the status code is 0.

            RequestMalformed: If the status code is 400.

            RequestUnauthorized: If the status code is 401.

            RequestForbidden: If the status code is 403.

            ObjectNotFound: If the status code is 404.

            ObjectAlreadyExists: If the status code is 409.

            ObjectUnprocessable: If the status code is 422.

            ServerError: If the status code is 500.

            ServiceUnavailable: If the status code is 503.

            TypesenseClientError: If the status code is not one of the above.
        """
        num_tries = 0
        last_exception: BaseException

        logger.debug('Making {} {}'.format(fn.__name__, endpoint))

        while num_tries < (self.config.num_retries + 1):
            num_tries += 1
            node = self.get_node()

            logger.debug('Try {} to node {}:{} -- healthy? {}'.format(num_tries, node.host, node.port, node.healthy))

            try:
                url = node.url() + endpoint
                if kwargs.get('data') and not (isinstance(kwargs['data'], str) or isinstance(kwargs['data'], bytes)):
                    kwargs['data'] = json.dumps(kwargs['data'])

                r = fn(url, headers={ApiCall.API_KEY_HEADER_NAME: self.config.api_key}, **kwargs)

                # Treat any status code > 0 and < 500 to be an indication that node is healthy
                # We exclude 0 since some clients return 0 when request fails
                if 0 < r.status_code < 500:
                    logger.debug('{}:{} is healthy. Status code: {}'.format(node.host, node.port, r.status_code))
                    self.set_node_healthcheck(node, True)

                # We should raise a custom exception if status code is not 20X
                if not 200 <= r.status_code < 300:
                    if r.headers.get('Content-Type', '').startswith('application/json'):
                        error_message = r.json().get('message', 'API error.')
                    else:
                        error_message = 'API error.'
                    # Raised exception will be caught and retried
                    raise ApiCall.get_exception(r.status_code)(r.status_code, error_message)

                return r.json() if as_json else r.text
            except (
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
                requests.exceptions.HTTPError,
                requests.exceptions.RequestException,
                requests.exceptions.SSLError,
                exceptions.HTTPStatus0Error,
                exceptions.ServerError,
                exceptions.ServiceUnavailable,
            ) as e:
                # Catch the exception and retry
                self.set_node_healthcheck(node, False)
                logger.debug('Request to {}:{} failed because of {}'.format(node.host, node.port, e))
                logger.debug('Sleeping for {} and retrying...'.format(self.config.retry_interval_seconds))
                last_exception = e
                time.sleep(self.config.retry_interval_seconds)

        logger.debug('No retries left. Raising last exception: {}'.format(last_exception))
        raise last_exception

    def set_node_healthcheck(self, node: Node, is_healthy: bool) -> None:
        """
        Set the health status of the node and updates the last access timestamp.

        Args:
            node (Node): The node to set the health status of.
            is_healthy (bool): Whether the node is healthy
        """
        node.healthy = is_healthy
        node.last_access_ts = int(time.time())

    @staticmethod
    def normalize_params(params: TParams) -> None:
        """
        Normalize boolean values in the request parameters to strings.

        Args:
            params (TParams): The request parameters.
        """
        for key in params.keys():
            if isinstance(params[key], bool) and params[key]:
                params[key] = 'true'
            elif isinstance(params[key], bool) and not params[key]:
                params[key] = 'false'

    @typing.overload
    def get(
        self,
        endpoint: str,
        as_json: typing.Literal[False],
        params: TParams | None = None,
    ) -> str:
        """
        Make a GET request to the endpoint with the given parameters.

        Args:
            endpoint (str): The endpoint to make the request to.
            as_json = True: Whether to return the response as a JSON object.
            params (TParams | None): The request parameters.

        Returns:
            TEntityDict: The response from the request in json format

        :raises:
            HTTPStatus0Error: If the status code is 0.

            RequestMalformed: If the status code is 400.

            RequestUnauthorized: If the status code is 401.

            RequestForbidden: If the status code is 403.

            ObjectNotFound: If the status code is 404.

            ObjectAlreadyExists: If the status code is 409.

            ObjectUnprocessable: If the status code is 422.

            ServerError: If the status code is 500.

            ServiceUnavailable: If the status code is 503.

            TypesenseClientError: If the status code is not one of the above.
        """

    @typing.overload
    def get(
        self,
        endpoint: str,
        as_json: typing.Literal[True],
        params: TParams | None = None,
    ) -> TEntityDict:
        """
        Make a GET request to the endpoint with the given parameters.

        Args:
            endpoint (str): The endpoint to make the request to.
            as_json = False: Whether to return the response as a JSON object.
            params (TParams | None): The request parameters.

        Returns:
            str: The response from the request in text format

        :raises:
            HTTPStatus0Error: If the status code is 0.

            RequestMalformed: If the status code is 400.

            RequestUnauthorized: If the status code is 401.

            RequestForbidden: If the status code is 403.

            ObjectNotFound: If the status code is 404.

            ObjectAlreadyExists: If the status code is 409.

            ObjectUnprocessable: If the status code is 422.

            ServerError: If the status code is 500.

            ServiceUnavailable: If the status code is 503.

            TypesenseClientError: If the status code is not one of the above.
        """

    def get(
        self,
        endpoint: str,
        as_json: typing.Literal[True] | typing.Literal[False] = True,
        params: TParams | None = None,
    ) -> TEntityDict | str:
        """
        Make a GET request to the endpoint with the given parameters.

        Args:
            endpoint (str): The endpoint to make the request to.
            as_json (bool): Whether to return the response as a JSON object.
            params (TParams | None): The request parameters.

        Returns:
            Union[TEntityDict, str]: The response from the request

        :raises:
            HTTPStatus0Error: If the status code is 0.

            RequestMalformed: If the status code is 400.

            RequestUnauthorized: If the status code is 401.

            RequestForbidden: If the status code is 403.

            ObjectNotFound: If the status code is 404.

            ObjectAlreadyExists: If the status code is 409.

            ObjectUnprocessable: If the status code is 422.

            ServerError: If the status code is 500.

            ServiceUnavailable: If the status code is 503.

            TypesenseClientError: If the status code is not one of the above.
        """
        return self.make_request(
            session.get,
            endpoint,
            as_json=as_json,
            params=params,
            timeout=self.config.connection_timeout_seconds,
            verify=self.config.verify,
        )

    @typing.overload
    def post(
        self,
        endpoint: str,
        body: TBody,
        as_json: typing.Literal[False],
        params: TParams | None = None,
    ) -> str:
        """
        Make a POST request to the endpoint with the given parameters.

        Args:
            endpoint (str): The endpoint to make the request to.
            body (TBody): The request body.
            as_json = False: Whether to return the response as a JSON object.
            params (TParams | None): The request parameters.

        Returns:
            str: The response from the request in text format

        :raises:
            HTTPStatus0Error: If the status code is 0.

            RequestMalformed: If the status code is 400.

            RequestUnauthorized: If the status code is 401.

            RequestForbidden: If the status code is 403.

            ObjectNotFound: If the status code is 404.

            ObjectAlreadyExists: If the status code is 409.

            ObjectUnprocessable: If the status code is 422.

            ServerError: If the status code is 500.

            ServiceUnavailable: If the status code is 503.

            TypesenseClientError: If the status code is not one of the above.
        """

    @typing.overload
    def post(
        self,
        endpoint: str,
        body: TBody,
        as_json: typing.Literal[True],
        params: TParams | None = None,
    ) -> TEntityDict:
        """
        Make a POST request to the endpoint with the given parameters.

        Args:
            endpoint (str): The endpoint to make the request to.
            body (TBody): The request body.
            as_json = True: Whether to return the response as a JSON object.
            params (TParams | None): The request parameters.

        Returns:
            TEntityDict: The response from the request in json format

        :raises:
            HTTPStatus0Error: If the status code is 0.

            RequestMalformed: If the status code is 400.

            RequestUnauthorized: If the status code is 401.

            RequestForbidden: If the status code is 403.

            ObjectNotFound: If the status code is 404.

            ObjectAlreadyExists: If the status code is 409.

            ObjectUnprocessable: If the status code is 422.

            ServerError: If the status code is 500.

            ServiceUnavailable: If the status code is 503.

            TypesenseClientError: If the status code is not one of the above.
        """

    def post(
        self,
        endpoint: str,
        body: TBody,
        as_json: typing.Literal[True, False],
        params: TParams | None = None,
    ) -> str | TEntityDict:
        """
        Make a POST request to the endpoint with the given parameters.

        Args:
            endpoint (str): The endpoint to make the request to.
            body (TBody): The request body.
            as_json = bool: Whether to return the response as a JSON object.
            params (TParams | None): The request parameters.

        Returns:
            TEntityDict | str: The response from the request

        :raises:
            HTTPStatus0Error: If the status code is 0.

            RequestMalformed: If the status code is 400.

            RequestUnauthorized: If the status code is 401.

            RequestForbidden: If the status code is 403.

            ObjectNotFound: If the status code is 404.

            ObjectAlreadyExists: If the status code is 409.

            ObjectUnprocessable: If the status code is 422.

            ServerError: If the status code is 500.

            ServiceUnavailable: If the status code is 503.

            TypesenseClientError: If the status code is not one of the above.
        """
        if params:
            ApiCall.normalize_params(params)
        return self.make_request(
            session.post,
            endpoint,
            as_json=as_json,
            params=params,
            data=body,
            timeout=self.config.connection_timeout_seconds,
            verify=self.config.verify,
        )

    def put(
        self,
        endpoint: str,
        body: TBody,
        params: TParams | None = None,
    ) -> TEntityDict:
        """
        Make a PUT request to the endpoint with the given parameters.

        Args:
            endpoint (str): The endpoint to make the request to.
            body (TBody): The request body.
            params (TParams | None): The request parameters.

        Returns:
            TEntityDict: The response from the request in json format

        :raises:
            HTTPStatus0Error: If the status code is 0.

            RequestMalformed: If the status code is 400.

            RequestUnauthorized: If the status code is 401.

            RequestForbidden: If the status code is 403.

            ObjectNotFound: If the status code is 404.

            ObjectAlreadyExists: If the status code is 409.

            ObjectUnprocessable: If the status code is 422.

            ServerError: If the status code is 500.

            ServiceUnavailable: If the status code is 503.

            TypesenseClientError: If the status code is not one of the above.
        """
        return self.make_request(
            session.put,
            endpoint,
            True,
            params=params,
            data=body,
            timeout=self.config.connection_timeout_seconds,
            verify=self.config.verify,
        )

    def patch(
        self,
        endpoint: str,
        body: TBody,
        params: TParams | None = None,
    ) -> TEntityDict:
        """
        Make a PATCH request to the endpoint with the given parameters.

        Args:
            endpoint (str): The endpoint to make the request to.
            body (TBody): The request body.
            params (TParams | None): The request parameters.

        Returns:
            TEntityDict: The response from the request in json format

        :raises:
            HTTPStatus0Error: If the status code is 0.

            RequestMalformed: If the status code is 400.

            RequestUnauthorized: If the status code is 401.

            RequestForbidden: If the status code is 403.

            ObjectNotFound: If the status code is 404.

            ObjectAlreadyExists: If the status code is 409.

            ObjectUnprocessable: If the status code is 422.

            ServerError: If the status code is 500.

            ServiceUnavailable: If the status code is 503.

            TypesenseClientError: If the status code is not one of the above.
        """
        return self.make_request(
            session.patch,
            endpoint,
            True,
            params=params,
            data=body,
            timeout=self.config.connection_timeout_seconds,
            verify=self.config.verify,
        )

    def delete(self, endpoint: str, params: TParams | None = None) -> TEntityDict:
        """
        Make a DELETE request to the endpoint with the given parameters.

        Args:
            endpoint (str): The endpoint to make the request to.
            params (TParams | None): The request parameters.

        Returns:
            TEntityDict: The response from the request in json format

        :raises:
            HTTPStatus0Error: If the status code is 0.

            RequestMalformed: If the status code is 400.

            RequestUnauthorized: If the status code is 401.

            RequestForbidden: If the status code is 403.

            ObjectNotFound: If the status code is 404.

            ObjectAlreadyExists: If the status code is 409.

            ObjectUnprocessable: If the status code is 422.

            ServerError: If the status code is 500.

            ServiceUnavailable: If the status code is 503.

            TypesenseClientError: If the status code is not one of the above.
        """
        return self.make_request(
            session.delete,
            endpoint,
            True,
            params=params,
            timeout=self.config.connection_timeout_seconds,
            verify=self.config.verify,
        )
