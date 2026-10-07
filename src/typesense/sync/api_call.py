"""
This module provides async functionality for making API calls to a Typesense server.

It contains the ApiCall class, which is responsible for executing async HTTP requests
to the Typesense API, handling retries, and managing node health.

Key features:
- Support for GET, POST, PUT, PATCH, and DELETE HTTP methods (async)
- Automatic retries on server errors
- Node health management
- Type-safe request execution with overloaded methods

Classes:
    ApiCall: Manages async API calls to the Typesense server.

Dependencies:
    - httpx: For making async HTTP requests
    - typesense.configuration: Provides Configuration and Node classes
    - typesense.exceptions: Custom exception classes
    - typesense.node_manager: Provides NodeManager class

Usage:
    from typesense.configuration import Configuration
    from .api_call import ApiCall

    config = Configuration(...)
    api_call = ApiCall(config)
    response = await api_call.get("/collections", SomeEntityType)

Note: This module is part of the Typesense Python client library and is used internally
by other components of the library.
"""

import time
import sys
from types import MappingProxyType, TracebackType

import httpx

from typesense.configuration import Configuration, Node
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
from typesense.node_manager import NodeManager
from typesense.request_handler import RequestHandler

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

TEntityDict = typing.TypeVar("TEntityDict")
TParams = typing.TypeVar("TParams", bound=typing.Dict[str, typing.Any])
TBody = typing.TypeVar(
    "TBody", bound=typing.Union[str, bytes, typing.Mapping[str, typing.Any]]
)


class SessionFunctionKwargs(typing.Generic[TParams, TBody], typing.TypedDict):
    """
    Type definition for keyword arguments used in request functions.

    This is an internal abstraction that gets converted to httpx's request parameters.
    The `data` field is converted to `content` when passed to httpx.

    Note: `verify` and `timeout` are set on the httpx client, not in request kwargs.
    However, we include them here for compatibility with the existing API.

    Attributes:
        params (Optional[Union[TParams, None]]): Query parameters for the request.
            Passed as `params` to httpx.

        data (Optional[Union[TBody, str, None]]): Body of the request.
            Converted to `content` (JSON string) when passed to httpx.

        headers (Optional[Dict[str, str]]): Headers for the request.
            Passed as `headers` to httpx.

        timeout (float): Timeout for the request in seconds.
            Set on the httpx client, not in request kwargs.

        verify (bool): Whether to verify SSL certificates.
            Set on the httpx client, not in request kwargs.
    """

    params: typing.NotRequired[typing.Union[TParams, None]]
    data: typing.NotRequired[typing.Union[TBody, None]]
    content: typing.NotRequired[typing.Union[TBody, str, None]]
    headers: typing.NotRequired[typing.Dict[str, str]]
    timeout: typing.NotRequired[float]


_ERROR_CODE_MAP: typing.Final[
    typing.Mapping[str, typing.Type[TypesenseClientError]]
] = MappingProxyType(
    {
        "0": HTTPStatus0Error,
        "400": RequestMalformed,
        "401": RequestUnauthorized,
        "403": RequestForbidden,
        "404": ObjectNotFound,
        "409": ObjectAlreadyExists,
        "422": ObjectUnprocessable,
        "500": ServerError,
        "503": ServiceUnavailable,
    },
)

_SERVER_ERRORS: typing.Final[
    typing.Tuple[
        typing.Type[httpx.TimeoutException],
        typing.Type[httpx.ConnectError],
        typing.Type[httpx.HTTPError],
        typing.Type[httpx.RequestError],
        typing.Type[HTTPStatus0Error],
        typing.Type[ServerError],
        typing.Type[ServiceUnavailable],
    ]
] = (
    httpx.TimeoutException,
    httpx.ConnectError,
    httpx.HTTPError,
    httpx.RequestError,
    HTTPStatus0Error,
    ServerError,
    ServiceUnavailable,
)


class ApiCall:
    """
    Manages async API calls to the Typesense server.

    This class handles the execution of async HTTP requests to the Typesense API,
    including retries, node health management, and error handling.

    Attributes:
        config (Configuration): The configuration object for the Typesense client.
        node_manager (NodeManager): Manages the nodes in the Typesense cluster.
        _client (httpx.Client): The httpx async client for making requests.
    """

    def __init__(self, config: Configuration):
        """
        Initialize the ApiCall instance.

        Args:
            config (Configuration): The configuration object for the Typesense client.
        """
        self.config = config
        self.node_manager = NodeManager(config)
        self.request_handler = RequestHandler(config)
        self._client = httpx.Client(
            timeout=config.connection_timeout_seconds,
        )

    def __enter__(self) -> "ApiCall":
        """Async context manager entry."""
        return self

    def __exit__(
        self,
        exc_type: typing.Optional[typing.Type[BaseException]],
        exc_val: typing.Optional[BaseException],
        exc_tb: typing.Optional[TracebackType],
    ) -> None:
        """Async context manager exit."""
        self._client.close()

    def close(self) -> None:
        """Close the httpx client."""
        self._client.close()

    @typing.overload
    def get(
        self,
        endpoint: str,
        entity_type: typing.Type[TEntityDict],
        as_json: typing.Literal[False],
        params: typing.Union[TParams, None] = None,
    ) -> str:
        """
        Execute an async GET request to the Typesense API.

        Args:
            endpoint (str): The API endpoint to call.
            entity_type (Type[TEntityDict]): The expected type of the response entity.
            as_json (False): Whether to return the response as JSON. Defaults to True.
            params (Union[TParams, None], optional): Query parameters for the request.

        Returns:
            str: The response, as a string.
        """

    @typing.overload
    def get(
        self,
        endpoint: str,
        entity_type: typing.Type[TEntityDict],
        as_json: typing.Literal[True] = True,
        params: typing.Union[TParams, None] = None,
    ) -> TEntityDict:
        """
        Execute an async GET request to the Typesense API.

        Args:
            endpoint (str): The API endpoint to call.
            entity_type (Type[TEntityDict]): The expected type of the response entity.
            as_json (True): Whether to return the response as JSON. Defaults to True.
            params (Union[TParams, None], optional): Query parameters for the request.

        Returns:
            EntityDict: The response, as a JSON object.
        """

    def get(
        self,
        endpoint: str,
        entity_type: typing.Type[TEntityDict],
        as_json: typing.Union[typing.Literal[True], typing.Literal[False]] = True,
        params: typing.Union[TParams, None] = None,
    ) -> typing.Union[TEntityDict, str]:
        """
        Execute an async GET request to the Typesense API.

        Args:
            endpoint (str): The API endpoint to call.
            entity_type (Type[TEntityDict]): The expected type of the response entity.
            as_json (bool): Whether to return the response as JSON. Defaults to True.
            params (Union[TParams, None], optional): Query parameters for the request.

        Returns:
            Union[TEntityDict, str]: The response, either as a JSON object or a string.
        """
        return self._execute_request(
            "GET",
            endpoint,
            entity_type,
            as_json,
            params=params,
        )

    @typing.overload
    def post(
        self,
        endpoint: str,
        entity_type: typing.Type[TEntityDict],
        as_json: typing.Literal[False],
        params: typing.Union[TParams, None] = None,
        body: typing.Union[TBody, None] = None,
    ) -> str:
        """
        Execute an async POST request to the Typesense API.

        Args:
            endpoint (str): The API endpoint to call.
            entity_type (Type[TEntityDict]): The expected type of the response entity.
            as_json (False): Whether to return the response as JSON. Defaults to True.
            params (Union[TParams, None], optional): Query parameters for the request.
            body (Union[TBody, None], optional): Request body.

        Returns:
            str: The response, as a string.
        """

    @typing.overload
    def post(
        self,
        endpoint: str,
        entity_type: typing.Type[TEntityDict],
        as_json: typing.Literal[True] = True,
        params: typing.Union[TParams, None] = None,
        body: typing.Union[TBody, None] = None,
    ) -> TEntityDict:
        """
        Execute an async POST request to the Typesense API.

        Args:
            endpoint (str): The API endpoint to call.
            entity_type (Type[TEntityDict]): The expected type of the response entity.
            as_json (True): Whether to return the response as JSON. Defaults to True.
            params (Union[TParams, None], optional): Query parameters for the request.
            body (Union[TBody, None], optional): Request body.

        Returns:
            EntityDict: The response, as a JSON object.
        """

    def post(
        self,
        endpoint: str,
        entity_type: typing.Type[TEntityDict],
        as_json: typing.Union[typing.Literal[True], typing.Literal[False]] = True,
        params: typing.Union[TParams, None] = None,
        body: typing.Union[TBody, None] = None,
    ) -> typing.Union[str, TEntityDict]:
        """
        Execute an async POST request to the Typesense API.

        Args:
            endpoint (str): The API endpoint to call.
            entity_type (Type[TEntityDict]): The expected type of the response entity.
            as_json (bool): Whether to return the response as JSON. Defaults to True.
            params (Union[TParams, None], optional): Query parameters for the request.
            body (Union[TBody, None], optional): Request body.

        Returns:
            Union[TEntityDict, str]: The response, either as a JSON object or a string.
        """
        return self._execute_request(
            "POST",
            endpoint,
            entity_type,
            as_json,
            params=params,
            data=body,
        )

    def put(
        self,
        endpoint: str,
        entity_type: typing.Type[TEntityDict],
        body: TBody,
        params: typing.Union[TParams, None] = None,
    ) -> TEntityDict:
        """
        Execute an async PUT request to the Typesense API.

        Args:
            endpoint (str): The API endpoint to call.
            entity_type (Type[TEntityDict]): The expected type of the response entity.
            params (Union[TParams, None], optional): Query parameters for the request.
            body (TBody): Request body.

        Returns:
            EntityDict: The response, as a JSON object.
        """
        return self._execute_request(
            "PUT",
            endpoint,
            entity_type,
            as_json=True,
            params=params,
            data=body,
        )

    def patch(
        self,
        endpoint: str,
        entity_type: typing.Type[TEntityDict],
        body: TBody,
        params: typing.Union[TParams, None] = None,
    ) -> TEntityDict:
        """
        Execute an async PATCH request to the Typesense API.

        Args:
            endpoint (str): The API endpoint to call.
            entity_type (Type[TEntityDict]): The expected type of the response entity.
            params (Union[TParams, None], optional): Query parameters for the request.
            body (TBody): Request body.

        Returns:
            EntityDict: The response, as a JSON object.
        """
        return self._execute_request(
            "PATCH",
            endpoint,
            entity_type,
            as_json=True,
            params=params,
            data=body,
        )

    def delete(
        self,
        endpoint: str,
        entity_type: typing.Type[TEntityDict],
        params: typing.Union[TParams, None] = None,
    ) -> TEntityDict:
        """
        Execute an async DELETE request to the Typesense API.

        Args:
            endpoint (str): The API endpoint to call.
            entity_type (Type[TEntityDict]): The expected type of the response entity.
            params (Union[TParams, None], optional): Query parameters for the request.

        Returns:
            EntityDict: The response, as a JSON object.
        """
        return self._execute_request(
            "DELETE",
            endpoint,
            entity_type,
            as_json=True,
            params=params,
        )

    @typing.overload
    def _execute_request(
        self,
        method: str,
        endpoint: str,
        entity_type: typing.Type[TEntityDict],
        as_json: typing.Literal[True],
        last_exception: typing.Union[None, Exception] = None,
        num_retries: int = 0,
        **kwargs: typing.Unpack[SessionFunctionKwargs[TParams, TBody]],
    ) -> TEntityDict:
        """Execute an async request with retry logic."""

    @typing.overload
    def _execute_request(
        self,
        method: str,
        endpoint: str,
        entity_type: typing.Type[TEntityDict],
        as_json: typing.Literal[False],
        last_exception: typing.Union[None, Exception] = None,
        num_retries: int = 0,
        **kwargs: typing.Unpack[SessionFunctionKwargs[TParams, TBody]],
    ) -> str:
        """Execute an async request with retry logic."""

    def _execute_request(
        self,
        method: str,
        endpoint: str,
        entity_type: typing.Type[TEntityDict],
        as_json: typing.Union[typing.Literal[True], typing.Literal[False]] = True,
        last_exception: typing.Union[None, Exception] = None,
        num_retries: int = 0,
        **kwargs: typing.Unpack[SessionFunctionKwargs[TParams, TBody]],
    ) -> typing.Union[TEntityDict, str]:
        """
        Execute an async request to the Typesense API with retry logic.

        This method handles the actual execution of the request, including
        node selection, error handling, and retries.

        Args:
            method (str): The HTTP method to use (GET, POST, PUT, PATCH, DELETE).
            endpoint (str): The API endpoint to call.
            entity_type (Type[TEntityDict]): The expected type of the response entity.
            as_json (bool): Whether to return the response as JSON. Defaults to True.
            last_exception (Union[None, Exception], optional): The last exception encountered.
            num_retries (int): The current number of retries attempted.
            kwargs: Additional keyword arguments for the request.

        Returns:
            Union[TEntityDict, str]: The response, either as a JSON object or a string.

        Raises:
            TypesenseClientError: If all nodes are unhealthy or max retries are exceeded.
        """
        if num_retries > self.config.num_retries:
            if last_exception:
                raise last_exception
            raise TypesenseClientError("All nodes are unhealthy")

        node, url, request_kwargs = self._prepare_request_params(endpoint, **kwargs)

        try:
            return self._make_request_and_process_response(
                method,
                url,
                entity_type,
                as_json,
                **request_kwargs,
            )
        except _SERVER_ERRORS as server_error:
            self.node_manager.set_node_health(node, is_healthy=False)
            if num_retries < self.config.num_retries:
                time.sleep(self.config.retry_interval_seconds)
            return self._execute_request(
                method,
                endpoint,
                entity_type,
                as_json,
                last_exception=server_error,
                num_retries=num_retries + 1,
                **kwargs,
            )

    def _make_request_and_process_response(
        self,
        method: str,
        url: str,
        entity_type: typing.Type[TEntityDict],
        as_json: bool,
        **kwargs: typing.Unpack[SessionFunctionKwargs[TParams, TBody]],
    ) -> typing.Union[TEntityDict, str]:
        """Make the async API request and process the response."""
        request_response = self.request_handler.make_request(
            method=method,
            url=url,
            as_json=as_json,
            entity_type=entity_type,
            client=self._client,
            **kwargs,
        )
        self.node_manager.set_node_health(
            self.node_manager.get_node(),
            is_healthy=True,
        )
        return (
            typing.cast(TEntityDict, request_response)
            if as_json
            else typing.cast(str, request_response)
        )

    def _prepare_request_params(
        self,
        endpoint: str,
        **kwargs: typing.Unpack[SessionFunctionKwargs[TParams, TBody]],
    ) -> typing.Tuple[Node, str, SessionFunctionKwargs[TParams, TBody]]:
        """
        Prepare request parameters including node selection and URL construction.

        Args:
            endpoint: The API endpoint path.
            **kwargs: Request parameters following SessionFunctionKwargs structure.

        Returns:
            Tuple of (node, full_url, kwargs_dict) where kwargs_dict contains
            the request parameters as a regular dict for further processing.
        """
        node = self.node_manager.get_node()
        url = node.url() + endpoint

        if params := kwargs.get("params"):
            self.request_handler.normalize_params(params)

        return node, url, kwargs
