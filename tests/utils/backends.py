"""
The HTTP backends that the streaming tests run against.

``httpx`` and ``httpx2`` have the same API but separate classes, so a test written
once for both cannot be typed with either module. ``Backend`` is a typed view of the
parts the tests use, under the modules' own names, built once for each module.
"""

import dataclasses
import sys

import httpx
import pytest

from typesense.http_backend import AsyncClientType, ResponseType, SyncClientType

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

if typing.TYPE_CHECKING:
    import httpx2

RequestType = typing.Union[httpx.Request, "httpx2.Request"]
Handler = typing.Callable[[RequestType], ResponseType]
AsyncHandler = typing.Callable[[RequestType], typing.Awaitable[ResponseType]]
ResponseContent = typing.Union[
    bytes,
    typing.Iterator[bytes],
    typing.AsyncIterator[bytes],
]


class ResponseFactory(typing.Protocol):
    """Builds a response the way ``httpx.Response`` does."""

    def __call__(
        self,
        status_code: int,
        *,
        headers: typing.Optional[typing.Mapping[str, str]] = None,
        content: typing.Optional[ResponseContent] = None,
        text: typing.Optional[str] = None,
        json: object = None,
    ) -> ResponseType:
        """Return a response with ``status_code`` and the given body."""


@dataclasses.dataclass(frozen=True)
class Backend:
    """The parts of ``httpx`` or ``httpx2`` that the tests use."""

    Response: ResponseFactory
    ReadError: typing.Union[
        typing.Type[httpx.ReadError],
        typing.Type["httpx2.ReadError"],
    ]
    RemoteProtocolError: typing.Union[
        typing.Type[httpx.RemoteProtocolError],
        typing.Type["httpx2.RemoteProtocolError"],
    ]
    client: typing.Callable[[Handler], SyncClientType]
    async_client: typing.Callable[[AsyncHandler], AsyncClientType]


def load_backend(name: str) -> Backend:
    """Return the backend called ``name``, skipping the test if it is not installed."""
    if name == "httpx":
        return _httpx_backend()
    pytest.importorskip("httpx2")
    return _httpx2_backend()


def _httpx_backend() -> Backend:
    """Return ``httpx`` as a ``Backend``."""

    def client(handler: Handler) -> httpx.Client:
        def respond(request: httpx.Request) -> httpx.Response:
            response = handler(request)
            assert isinstance(response, httpx.Response)
            return response

        return httpx.Client(transport=httpx.MockTransport(respond))

    def async_client(handler: AsyncHandler) -> httpx.AsyncClient:
        async def respond(request: httpx.Request) -> httpx.Response:
            response = await handler(request)
            assert isinstance(response, httpx.Response)
            return response

        return httpx.AsyncClient(transport=httpx.MockTransport(respond))

    return Backend(
        Response=httpx.Response,
        ReadError=httpx.ReadError,
        RemoteProtocolError=httpx.RemoteProtocolError,
        client=client,
        async_client=async_client,
    )


def _httpx2_backend() -> Backend:
    """Return ``httpx2`` as a ``Backend``. It is imported here, being optional."""
    import httpx2  # noqa: WPS433

    def client(handler: Handler) -> httpx2.Client:
        def respond(request: httpx2.Request) -> httpx2.Response:
            response = handler(request)
            assert isinstance(response, httpx2.Response)
            return response

        return httpx2.Client(transport=httpx2.MockTransport(respond))

    def async_client(handler: AsyncHandler) -> httpx2.AsyncClient:
        async def respond(request: httpx2.Request) -> httpx2.Response:
            response = await handler(request)
            assert isinstance(response, httpx2.Response)
            return response

        return httpx2.AsyncClient(transport=httpx2.MockTransport(respond))

    return Backend(
        Response=httpx2.Response,
        ReadError=httpx2.ReadError,
        RemoteProtocolError=httpx2.RemoteProtocolError,
        client=client,
        async_client=async_client,
    )
