"""
This module provides functionality for handling HTTP requests in the Typesense client library.

Classes:
    - RequestHandler: Manages HTTP requests to the Typesense API (supports both sync and async).
    - SessionFunctionKwargs: Type for keyword arguments in session functions.

The RequestHandler class interacts with the Typesense API to manage HTTP requests,
handle authentication, and process responses. It provides methods to send requests,
normalize parameters, and handle errors. It supports both sync (httpx.Client) and async (httpx.AsyncClient) clients.

This module uses type hinting and is compatible with Python 3.11+ as well as earlier
versions through the use of the typing_extensions library.

Key Features:
- Handles authentication via API key
- Supports JSON and non-JSON responses
- Provides custom error handling for various HTTP status codes
- Normalizes boolean parameters for API requests
- Supports both sync (httpx.Client) and async (httpx.AsyncClient) HTTP clients

Note: This module relies on the 'httpx' library for both sync and async operations.
"""

import json
import sys
from types import MappingProxyType

import httpx

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

from typesense.configuration import Configuration
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

TEntityDict = typing.TypeVar("TEntityDict")
TParams = typing.TypeVar("TParams", bound=typing.Dict[str, typing.Any])
TBody = typing.TypeVar("TBody", bound=typing.Union[str, bytes])

_ERROR_CODE_MAP: typing.Mapping[str, typing.Type[TypesenseClientError]] = (
    MappingProxyType(
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
    data: typing.NotRequired[
        typing.Union[TBody, str, typing.Dict[str, typing.Any], None]
    ]
    content: typing.NotRequired[typing.Union[TBody, str, None]]
    headers: typing.NotRequired[typing.Dict[str, str]]
    timeout: typing.NotRequired[float]


class RequestHandler:
    """
    Handles HTTP requests to the Typesense API (supports both sync and async using httpx).

    This class manages authentication, request sending, and response processing
    for interactions with the Typesense API. It can work with both sync (httpx.Client)
    and async (httpx.AsyncClient) HTTP clients.

    Attributes:
        api_key_header_name (str): The header name for the API key.
        config (Configuration): The configuration object for the Typesense client.
    """

    api_key_header_name: typing.Final[str] = "X-TYPESENSE-API-KEY"

    def __init__(self, config: Configuration):
        """
        Initialize the RequestHandler with a configuration.

        Args:
            config (Configuration): The configuration object for the Typesense client.
        """
        self.config = config

    def make_request(
        self,
        *,
        method: str,
        url: str,
        entity_type: typing.Type[TEntityDict],
        as_json: typing.Union[typing.Literal[True], typing.Literal[False]] = True,
        client: typing.Union[httpx.Client, httpx.AsyncClient],
        **kwargs: typing.Unpack[SessionFunctionKwargs[TParams, TBody]],
    ) -> typing.Union[
        TEntityDict,
        str,
        typing.Coroutine[typing.Any, typing.Any, typing.Union[TEntityDict, str]],
    ]:
        """
        Make an HTTP request to the Typesense API (supports both sync and async using httpx).

        Args:
            method (str): The HTTP method (e.g., "GET", "POST", "PUT", "PATCH", "DELETE").

            url (str): The URL to send the request to.

            entity_type (Type[TEntityDict]): The expected type of the response entity.

            as_json (bool): Whether to return the response as JSON. Defaults to True.

            client: The httpx client to use (httpx.Client for sync, httpx.AsyncClient for async).

            kwargs: Additional keyword arguments for the request.

        Returns:
            Union[TEntityDict, str]: The response, either as a JSON object or a string.
            If using AsyncClient, returns a coroutine.

        Raises:
            TypesenseClientError: If the API returns an error response.
        """
        headers = {
            self.api_key_header_name: self.config.api_key,
        }
        headers.update(self.config.additional_headers)

        request_kwargs: SessionFunctionKwargs[TParams, TBody] = typing.cast(
            SessionFunctionKwargs[TParams, TBody],
            {
                "headers": headers,
                "timeout": self.config.connection_timeout_seconds,
            },
        )

        if params := kwargs.get("params"):
            self.normalize_params(params)
            request_kwargs["params"] = params

        if body := kwargs.get("data"):
            if not isinstance(body, (str, bytes)):
                body = json.dumps(body)
            request_kwargs["content"] = typing.cast(TBody, body)

        if isinstance(client, httpx.AsyncClient):
            return self._make_async_request(
                method, url, entity_type, as_json, client, **request_kwargs
            )
        else:
            return self._make_sync_request(
                method, url, entity_type, as_json, client, **request_kwargs
            )

    def _make_sync_request(
        self,
        method: str,
        url: str,
        entity_type: typing.Type[TEntityDict],
        as_json: bool,
        client: httpx.Client,
        **request_kwargs: typing.Unpack[SessionFunctionKwargs[TParams, TBody]],
    ) -> typing.Union[TEntityDict, str]:
        """Make a synchronous HTTP request using httpx.Client."""
        params: typing.Union[TParams, None] = request_kwargs.get("params")
        content: typing.Union[TBody, str, None] = request_kwargs.get("content")
        headers: typing.Dict[str, str] = request_kwargs.get("headers", {})

        response = client.request(
            method,
            url,
            params=params,
            content=content,
            headers=headers,
        )

        if response.status_code < 200 or response.status_code >= 300:
            error_message = self._get_error_message(response)
            raise self._get_exception(response.status_code)(
                response.status_code,
                error_message,
            )

        if as_json:
            res: TEntityDict = typing.cast(TEntityDict, response.json())
            return res

        return response.text

    async def _make_async_request(
        self,
        method: str,
        url: str,
        entity_type: typing.Type[TEntityDict],
        as_json: bool,
        client: httpx.AsyncClient,
        **request_kwargs: typing.Unpack[SessionFunctionKwargs[TParams, TBody]],
    ) -> typing.Union[TEntityDict, str]:
        """Make an asynchronous HTTP request using httpx.AsyncClient."""
        params: typing.Union[TParams, None] = request_kwargs.get("params")
        content: typing.Union[TBody, str, None] = request_kwargs.get("content")
        headers: typing.Dict[str, str] = request_kwargs.get("headers", {})

        response = await client.request(
            method,
            url,
            params=params,
            content=content,
            headers=headers,
        )

        if response.status_code < 200 or response.status_code >= 300:
            error_message = self._get_error_message(response)
            raise self._get_exception(response.status_code)(
                response.status_code,
                error_message,
            )

        if as_json:
            res: TEntityDict = typing.cast(TEntityDict, response.json())
            return res

        return response.text

    @staticmethod
    def normalize_params(params: typing.Dict[str, typing.Any]) -> None:
        """
        Normalize boolean parameters in the request.

        Args:
            params (Dict[str, Any]): The parameters to normalize.

        Raises:
            ValueError: If params is not a dictionary.
        """
        if not isinstance(params, typing.Dict):
            raise ValueError("Params must be a dictionary.")
        for key, parameter_value in params.items():
            if isinstance(parameter_value, bool):
                params[key] = str(parameter_value).lower()

    @staticmethod
    def _get_error_message(response: httpx.Response) -> str:
        """
        Extract the error message from an API response.

        Args:
            response (httpx.Response): The API response.

        Returns:
            str: The extracted error message or a default message.
        """
        content_type = response.headers.get("Content-Type", "")
        if content_type.startswith("application/json"):
            try:
                return typing.cast(str, response.json().get("message", "API error."))
            except (json.JSONDecodeError, httpx.DecodingError):
                return f"API error: Invalid JSON response: {response.text}"
        if response.text:
            return f"API error. {response.text}"
        return f"Unknown API error. Full Response: {response}"

    @staticmethod
    def _get_exception(http_code: int) -> typing.Type[TypesenseClientError]:
        """
        Map an HTTP status code to the appropriate exception type.

        Any 5xx code without a dedicated exception (e.g. 502, 504 from a proxy
        in front of a restarting node) maps to ServerError, so the request is
        retried on another node.

        Args:
            http_code (int): The HTTP status code.

        Returns:
            Type[TypesenseClientError]: The exception type corresponding to the status code.
        """
        default = ServerError if 500 <= http_code <= 599 else TypesenseClientError
        return _ERROR_CODE_MAP.get(str(http_code), default)
