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

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

from typesense.exceptions import (
    HTTPStatus0Error,
    ObjectAlreadyExists,
    ObjectNotFound,
    ObjectUnprocessable,
    RequestForbidden,
    RequestMalformed,
    RequestUnauthorized,
    ServerError,
    ServiceUnavailable,
    TypesenseClientError,
)
from typesense.logger import logger

session = requests.sessions.Session()
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


class ApiCall:
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

    API_KEY_HEADER_NAME = "X-TYPESENSE-API-KEY"

    def __init__(self, config: Configuration):
        """Initializes the ApiCall instance with the given configuration.

        Args:
            config (Configuration): The configuration for the API client.
        """
        self.config = config
        self.nodes = copy.deepcopy(self.config.nodes)
        self.node_index = 0
        self._initialize_nodes()

    def node_due_for_health_check(self, node: Node) -> bool:
        current_epoch_ts = int(time.time())
        due_for_check: bool = (
            current_epoch_ts - node.last_access_ts
        ) > self.config.healthcheck_interval_seconds
        if due_for_check:
            logger.debug(
                f"Node {node.host}:{node.port} is due for health check.",
            )
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
            if self.config.nearest_node.healthy or self.node_due_for_health_check(
                self.config.nearest_node,
            ):
                logger.debug("Using nearest node.")
                return self.config.nearest_node

        logger.debug(
            " ".join(
                [
                    "Nearest node is unhealthy or not due for health check.",
                    "Falling back to individual nodes.",
                ],
            ),
        )

        node_index = 0
        while node_index < len(self.nodes):
            node_index += 1
            node = self.nodes[self.node_index]
            self.node_index = (self.node_index + 1) % len(self.nodes)

            if node.healthy or self.node_due_for_health_check(node):
                return node

        # None of the nodes are marked healthy,
        # but some of them could have become healthy since last health check.
        # So we will just return the next node.
        logger.debug("No healthy nodes were found. Returning the next node.")
        return self.nodes[self.node_index]

    @staticmethod
    def get_exception(http_code: int) -> type[TypesenseClientError]:
        """
        Return the exception class for a given HTTP status code.

        Args:
            http_code (int): The HTTP status code.

        Returns:
            Type[TypesenseClientError]: The exception class for the given HTTP status code.
        """
        if http_code == 0:
            return HTTPStatus0Error
        elif http_code == 400:
            return RequestMalformed
        elif http_code == 401:
            return RequestUnauthorized
        elif http_code == 403:
            return RequestForbidden
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

    @typing.overload
    def make_request(
        self,
        fn: typing.Callable[..., requests.models.Response],
        endpoint: str,
        entity_type: type[TEntityDict],
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
        entity_type: type[TEntityDict],
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
        entity_type: type[TEntityDict],
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

        logger.debug(f"Making {fn.__name__} {endpoint}")

        while num_tries < (self.config.num_retries + 1):
            num_tries += 1
            node = self.get_node()

            logger.debug(
                f"Try {num_tries} to node {node.host}:{node.port} -- healthy? {node.healthy}",
            )

            try:
                url = node.url() + endpoint
                if kwargs.get("data") and not isinstance(kwargs["data"], (str, bytes)):
                    kwargs["data"] = json.dumps(kwargs["data"])

                response = fn(
                    url,
                    headers={ApiCall.API_KEY_HEADER_NAME: self.config.api_key},
                    **kwargs,
                )

                # Treat any status code > 0 and < 500 to be an indication that node is healthy
                # We exclude 0 since some clients return 0 when request fails
                if 0 < response.status_code < 500:
                    logger.debug(
                        "".join(
                            [
                                f"{node.host}:{node.port} is healthy.",
                                f"Status code: {response.status_code}",
                            ],
                        ),
                    )
                    self.set_node_healthcheck(node, is_healthy=True)

                # We should raise a custom exception if status code is not 20X
                if response.status_code < 200 or response.status_code >= 300:
                    content_type = response.headers.get("Content-Type", "")
                    error_message = (
                        response.json().get("message", "API error.")
                        if content_type.startswith("application/json")
                        else "API error."
                    )
                    # Raised exception will be caught and retried
                    raise ApiCall.get_exception(response.status_code)(
                        response.status_code,
                        error_message,
                    )

                if as_json:
                    # Have to use type hinting to avoid returning any
                    resposne_json: TEntityDict = response.json()
                    return resposne_json  # noqa: WPS331
                return response.text
            except (
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
                requests.exceptions.HTTPError,
                requests.exceptions.RequestException,
                requests.exceptions.SSLError,
                HTTPStatus0Error,
                ServerError,
                ServiceUnavailable,
            ) as e:
                # Catch the exception and retry
                self.set_node_healthcheck(node, is_healthy=False)
                logger.debug(
                    " ".join(
                        [
                            f"Request to {node.host}:{node.port} failed",
                            "because of {connection_error}",
                        ],
                    ),
                )
                logger.debug(
                    f"Sleeping for {self.config.retry_interval_seconds} and retrying...",
                )
                last_exception = e
                time.sleep(self.config.retry_interval_seconds)

        logger.debug(f"No retries left. Raising last exception: {last_exception}")
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
                params[key] = "true"
            elif isinstance(params[key], bool) and not params[key]:
                params[key] = "false"

    @typing.overload
    def get(
        self,
        endpoint: str,
        entity_type: type[TEntityDict],
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
        entity_type: type[TEntityDict],
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
        entity_type: type[TEntityDict],
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
            entity_type,
            as_json=as_json,
            params=params,
            timeout=self.config.connection_timeout_seconds,
            verify=self.config.verify,
        )

    @typing.overload
    def post(
        self,
        endpoint: str,
        entity_type: type[TEntityDict],
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
        entity_type: type[TEntityDict],
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
        entity_type: type[TEntityDict],
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
            entity_type,
            as_json=as_json,
            params=params,
            data=body,
            timeout=self.config.connection_timeout_seconds,
            verify=self.config.verify,
        )

    def put(
        self,
        endpoint: str,
        entity_type: type[TEntityDict],
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
            entity_type,
            as_json=True,
            params=params,
            data=body,
            timeout=self.config.connection_timeout_seconds,
            verify=self.config.verify,
        )

    def patch(
        self,
        endpoint: str,
        entity_type: type[TEntityDict],
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
            entity_type,
            as_json=True,
            params=params,
            data=body,
            timeout=self.config.connection_timeout_seconds,
            verify=self.config.verify,
        )

    def delete(
        self,
        endpoint: str,
        entity_type: type[TEntityDict],
        params: TParams | None = None,
    ) -> TEntityDict:
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
            entity_type,
            as_json=True,
            params=params,
            timeout=self.config.connection_timeout_seconds,
            verify=self.config.verify,
        )

    def _initialize_nodes(self) -> None:
        if self.config.nearest_node:
            self.set_node_healthcheck(self.config.nearest_node, is_healthy=True)

        for node in self.nodes:
            self.set_node_healthcheck(node, is_healthy=True)
