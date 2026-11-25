"""
This module provides async functionality for making API calls to a Typesense server.

It contains the AsyncApiCall class, which is responsible for executing async HTTP requests
to the Typesense API, handling retries, and managing node health.

Key features:
- Support for GET, POST, PUT, PATCH, and DELETE HTTP methods (async)
- Automatic retries on server errors
- Node health management
- Type-safe request execution with overloaded methods

Classes:
    AsyncApiCall: Manages async API calls to the Typesense server.

Dependencies:
    - httpx: For making async HTTP requests
    - typesense.configuration: Provides Configuration and Node classes
    - typesense.exceptions: Custom exception classes
    - typesense.node_manager: Provides NodeManager class

Usage:
    from typesense.configuration import Configuration
    from .api_call import AsyncApiCall

    config = Configuration(...)
    api_call = AsyncApiCall(config)
    response = await api_call.get("/collections", SomeEntityType)

Note: This module is part of the Typesense Python client library and is used internally
by other components of the library.
"""

import asyncio
import sys
from contextlib import AsyncExitStack
from types import MappingProxyType, TracebackType

import httpx

from typesense.concurrency_limit import AsyncConcurrencyLimit
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
from typesense.http_backend import (
    ASYNC_CLIENT_TYPES,
    AsyncClientType,
    ResponseType,
    backend_errors,
    verify_option,
)
from .stream import AsyncExportStream, AsyncSearchStream
from typesense.node_manager import NodeManager
from typesense.request_handler import RequestHandler, _QueryParams

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

TEntityDict = typing.TypeVar("TEntityDict")
TStream = typing.TypeVar("TStream")
TParams = typing.TypeVar("TParams", bound=typing.Mapping[str, object])
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
    content: typing.NotRequired[typing.Union[str, bytes, None]]
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

_SERVER_ERRORS: typing.Final[typing.Tuple[typing.Type[Exception], ...]] = (
    *backend_errors("TimeoutException"),
    *backend_errors("ConnectError"),
    *backend_errors("HTTPError"),
    *backend_errors("RequestError"),
    HTTPStatus0Error,
    ServerError,
    ServiceUnavailable,
)

# Raised by httpx inside the client, so they say nothing about the node's
# health. They subclass entries of _SERVER_ERRORS and must be caught first.
_CLIENT_ERRORS: typing.Final[typing.Tuple[typing.Type[Exception], ...]] = (
    *backend_errors("PoolTimeout"),
    *backend_errors("LocalProtocolError"),
    *backend_errors("DecodingError"),
    *backend_errors("TooManyRedirects"),
)


class AsyncApiCall:
    """
    Manages async API calls to the Typesense server.

    This class handles the execution of async HTTP requests to the Typesense API,
    including retries, node health management, and error handling.

    Attributes:
        config (Configuration): The configuration object for the Typesense client.
        node_manager (NodeManager): Manages the nodes in the Typesense cluster.
        _client (httpx.AsyncClient | httpx2.AsyncClient): The async client for
            making requests.
    """

    def __init__(
        self,
        config: Configuration,
        http_client: typing.Optional[AsyncClientType] = None,
    ):
        """
        Initialize the AsyncApiCall instance.

        Args:
            config (Configuration): The configuration object for the Typesense client.
            http_client (httpx.AsyncClient | httpx2.AsyncClient, optional): A client
                to send requests with instead of the default httpx client. The
                connection pool and ``verify`` settings in ``config`` are not
                applied to it, and it is not closed by ``aclose``.

        Raises:
            TypeError: If ``http_client`` is not an httpx or httpx2 async client.
        """
        self.config = config
        self.node_manager = NodeManager(config)
        self.request_handler = RequestHandler(config)
        self._concurrency_limit = AsyncConcurrencyLimit(
            config.max_concurrent_requests,
        )
        self._owns_client = http_client is None
        self._export_limit = AsyncConcurrencyLimit(self._max_open_exports(config))
        if http_client is not None:
            if not isinstance(http_client, ASYNC_CLIENT_TYPES):
                raise TypeError(
                    "`http_client` must be an httpx.AsyncClient or httpx2.AsyncClient.",
                )
            self._client: AsyncClientType = http_client
            return
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(
                config.connection_timeout_seconds,
                pool=config.pool_timeout_seconds,
            ),
            limits=httpx.Limits(
                max_connections=config.max_connections,
                max_keepalive_connections=config.max_keepalive_connections,
            ),
            verify=verify_option(config.verify),
        )

    def _max_open_exports(self, config: Configuration) -> typing.Optional[int]:
        """
        Return how many exports may be open at once, or ``None`` for no limit.

        An open export keeps a connection but not a concurrency slot, so exports
        get the connections the slots cannot use. There is no limit without
        ``max_concurrent_requests``, when the pool is unlimited or belongs to a
        client passed in by the caller, or when the slots alone can fill the pool,
        which leaves no connection to keep free.
        """
        max_concurrent_requests = config.max_concurrent_requests
        max_connections = config.max_connections
        if max_concurrent_requests is None or max_connections is None:
            return None
        if not self._owns_client:
            return None
        spare_connections = max_connections - max_concurrent_requests
        return spare_connections if spare_connections > 0 else None

    async def __aenter__(self) -> "AsyncApiCall":
        """Async context manager entry."""
        return self

    async def __aexit__(
        self,
        exc_type: typing.Optional[typing.Type[BaseException]],
        exc_val: typing.Optional[BaseException],
        exc_tb: typing.Optional[TracebackType],
    ) -> None:
        """Async context manager exit."""
        await self.aclose()

    async def aclose(self) -> None:
        """Close the httpx client, unless it was passed in by the caller."""
        if self._owns_client:
            await self._client.aclose()

    @typing.overload
    async def get(
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
    async def get(
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

    async def get(
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
        return await self._execute_request(
            "GET",
            endpoint,
            entity_type,
            as_json,
            params=params,
        )

    @typing.overload
    async def post(
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
    async def post(
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

    async def post(
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
        return await self._execute_request(
            "POST",
            endpoint,
            entity_type,
            as_json,
            params=params,
            data=body,
        )

    async def put(
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
        return await self._execute_request(
            "PUT",
            endpoint,
            entity_type,
            as_json=True,
            params=params,
            data=body,
        )

    async def patch(
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
        return await self._execute_request(
            "PATCH",
            endpoint,
            entity_type,
            as_json=True,
            params=params,
            data=body,
        )

    async def delete(
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
        return await self._execute_request(
            "DELETE",
            endpoint,
            entity_type,
            as_json=True,
            params=params,
        )

    @typing.overload
    async def _execute_request(
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
    async def _execute_request(
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

    async def _execute_request(
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
            return await self._make_request_and_process_response(
                method,
                node,
                url,
                entity_type,
                as_json,
                **request_kwargs,
            )
        except _CLIENT_ERRORS:
            raise
        except _SERVER_ERRORS as server_error:
            self.node_manager.set_node_health(node, is_healthy=False)
            if num_retries < self.config.num_retries:
                await asyncio.sleep(self.config.retry_interval_seconds)
            return await self._execute_request(
                method,
                endpoint,
                entity_type,
                as_json,
                last_exception=server_error,
                num_retries=num_retries + 1,
                **kwargs,
            )

    async def _make_request_and_process_response(
        self,
        method: str,
        node: Node,
        url: str,
        entity_type: typing.Type[TEntityDict],
        as_json: bool,
        **kwargs: typing.Unpack[SessionFunctionKwargs[TParams, TBody]],
    ) -> typing.Union[TEntityDict, str]:
        """Make the async API request to `node` and process the response."""
        async with self._concurrency_limit:
            request_response = await self.request_handler.make_request(
                method=method,
                url=url,
                as_json=as_json,
                entity_type=entity_type,
                client=self._client,
                **kwargs,
            )
        self.node_manager.set_node_health(node, is_healthy=True)
        return (
            typing.cast(TEntityDict, request_response)
            if as_json
            else typing.cast(str, request_response)
        )

    async def stream(
        self,
        method: str,
        endpoint: str,
        entity_type: typing.Type[TEntityDict],
        params: typing.Union[TParams, None] = None,
        body: typing.Union[TBody, None] = None,
    ) -> AsyncSearchStream[TEntityDict]:
        """
        Open a streaming request to the Typesense API.

        Failing nodes are retried like any other request until the response
        headers arrive. Errors after that are raised while reading the stream and
        are not retried, since part of the answer has already been read.

        Args:
            method (str): The HTTP method to use.
            endpoint (str): The API endpoint to call.
            entity_type (Type[TEntityDict]): The type of the final response.
            params (Union[TParams, None], optional): Query parameters for the request.
            body (Union[TBody, None], optional): The request body.

        Returns:
            AsyncSearchStream[TEntityDict]: The open stream.
        """
        return await self._execute_stream_request(
            endpoint,
            lambda node, url, request_kwargs: self._open_search_stream(
                method,
                node,
                url,
                entity_type,
                **request_kwargs,
            ),
            params=params,
            data=body,
        )

    async def export_stream(
        self,
        endpoint: str,
        params: typing.Union[TParams, None] = None,
        *,
        compress: bool = False,
    ) -> AsyncExportStream:
        """
        Open a document export as a stream.

        The export takes its place among the open exports before a node is chosen,
        and keeps it until the stream is closed or its body ends or fails. Failing
        nodes are retried like any other request until the response headers
        arrive. Errors after that are raised while reading the stream and are not
        retried, since part of the export has already been read.

        Args:
            endpoint (str): The export endpoint to call.
            params (Union[TParams, None], optional): Query parameters for the request.
            compress (bool): Whether to let the server compress the response.

        Returns:
            AsyncExportStream: The open stream.
        """
        # Closes the response, then gives back the export's place.
        export = AsyncExitStack()
        await self._export_limit.acquire()
        export.callback(self._export_limit.release)
        try:
            response = await self._execute_stream_request(
                endpoint,
                lambda node, url, request_kwargs: self._open_export_stream(
                    export,
                    node,
                    url,
                    compress,
                    **request_kwargs,
                ),
                params=params,
            )
        except BaseException:
            await export.aclose()
            raise

        # A single entry, so that a second close cannot give back the place while
        # the first is still closing the response.
        exit_stack = AsyncExitStack()
        await exit_stack.enter_async_context(export)
        return AsyncExportStream(response, exit_stack)

    async def _execute_stream_request(
        self,
        endpoint: str,
        open_stream: typing.Callable[
            [Node, str, SessionFunctionKwargs[TParams, TBody]],
            typing.Awaitable[TStream],
        ],
        last_exception: typing.Union[None, Exception] = None,
        num_retries: int = 0,
        **kwargs: typing.Unpack[SessionFunctionKwargs[TParams, TBody]],
    ) -> TStream:
        """Open a streaming request, failing over to other nodes like ``_execute_request``."""
        if num_retries > self.config.num_retries:
            if last_exception:
                raise last_exception
            raise TypesenseClientError("All nodes are unhealthy")

        node, url, request_kwargs = self._prepare_request_params(endpoint, **kwargs)

        try:
            return await open_stream(node, url, request_kwargs)
        except _CLIENT_ERRORS:
            raise
        except _SERVER_ERRORS as server_error:
            self.node_manager.set_node_health(node, is_healthy=False)
            if num_retries < self.config.num_retries:
                await asyncio.sleep(self.config.retry_interval_seconds)
            return await self._execute_stream_request(
                endpoint,
                open_stream,
                last_exception=server_error,
                num_retries=num_retries + 1,
                **kwargs,
            )

    async def _open_search_stream(
        self,
        method: str,
        node: Node,
        url: str,
        entity_type: typing.Type[TEntityDict],
        **kwargs: typing.Unpack[SessionFunctionKwargs[TParams, TBody]],
    ) -> AsyncSearchStream[TEntityDict]:
        """
        Send a streaming search to `node` and return the stream once headers arrive.

        The stream holds a concurrency slot until it is closed. Reads use
        ``stream_read_timeout_seconds``, since the first piece of an answer only
        arrives once the LLM starts generating it.
        """
        request_kwargs = self.request_handler.build_request_kwargs(**kwargs)
        request_kwargs.setdefault("headers", {})["Accept"] = "text/event-stream"
        response_context = self._stream_context(method, url, request_kwargs)

        # Owns the concurrency slot and the response until the stream is closed.
        exit_stack = AsyncExitStack()
        await self._concurrency_limit.acquire()
        exit_stack.callback(self._concurrency_limit.release)
        try:
            response = await self._enter_stream(exit_stack, response_context)
        except BaseException:
            await exit_stack.aclose()
            raise

        self.node_manager.set_node_health(node, is_healthy=True)
        return AsyncSearchStream(response, exit_stack)

    async def _open_export_stream(
        self,
        export: AsyncExitStack,
        node: Node,
        url: str,
        compress: bool,
        **kwargs: typing.Unpack[SessionFunctionKwargs[TParams, TBody]],
    ) -> ResponseType:
        """
        Send an export request to `node` and return the response once headers arrive.

        The response is added to ``export``, which holds the export's place. The
        concurrency slot is held only while opening, so that a request made while
        reading the export does not have to wait for the export to finish.

        Unless ``compress`` is set the export is requested uncompressed, because
        the server compresses on the thread that handles every other request. An
        ``Accept-Encoding`` in ``additional_headers`` is left as it is.
        """
        request_kwargs = self.request_handler.build_request_kwargs(**kwargs)
        headers = request_kwargs.setdefault("headers", {})
        if not compress and "accept-encoding" not in map(str.lower, headers):
            headers["Accept-Encoding"] = "identity"
        response_context = self._stream_context("GET", url, request_kwargs)

        # Kept apart from ``export`` until the request succeeds, so that a failed
        # attempt closes its response without giving back the place.
        response_stack = AsyncExitStack()
        try:
            async with self._concurrency_limit:
                response = await self._enter_stream(response_stack, response_context)
        except BaseException:
            await response_stack.aclose()
            raise
        await export.enter_async_context(response_stack)

        self.node_manager.set_node_health(node, is_healthy=True)
        return response

    def _stream_context(
        self,
        method: str,
        url: str,
        request_kwargs: SessionFunctionKwargs[TParams, TBody],
    ) -> typing.AsyncContextManager[ResponseType]:
        """Return the context manager that sends a streaming request."""
        timeout = self._client.timeout
        # Annotated so httpx and httpx2 responses unify as ``ResponseType``.
        response_context: typing.AsyncContextManager[ResponseType] = (
            self._client.stream(
                method,
                url,
                params=typing.cast(
                    typing.Optional[_QueryParams],
                    request_kwargs.get("params"),
                ),
                content=request_kwargs.get("content"),
                headers=request_kwargs.get("headers"),
                timeout=(
                    timeout.connect,
                    self.config.stream_read_timeout_seconds,
                    timeout.write,
                    timeout.pool,
                ),
            )
        )
        return response_context

    async def _enter_stream(
        self,
        exit_stack: AsyncExitStack,
        response_context: typing.AsyncContextManager[ResponseType],
    ) -> ResponseType:
        """Send the request, raising the matching error for a non-2xx response."""
        response = await exit_stack.enter_async_context(response_context)
        if response.status_code < 200 or response.status_code >= 300:
            await response.aread()
            self.request_handler.raise_for_status(response)
        return response

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
