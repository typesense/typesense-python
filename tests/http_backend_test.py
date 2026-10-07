"""Tests for sending requests with a user-supplied httpx or httpx2 client."""

import sys

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

import httpx
import pytest

from typesense.async_.api_call import AsyncApiCall
from typesense.configuration import Configuration
from typesense.http_backend import ASYNC_CLIENT_TYPES, CLIENT_TYPES
from typesense.sync.api_call import ApiCall

httpx2 = pytest.importorskip("httpx2")


def _ok_response(request: typing.Any) -> typing.Any:
    """Return a successful JSON response."""
    return httpx2.Response(200, json={"key": "value"})


def test_backend_errors_include_httpx2() -> None:
    """Test that httpx2 clients are recognised when httpx2 is installed."""
    assert httpx2.Client in CLIENT_TYPES
    assert httpx2.AsyncClient in ASYNC_CLIENT_TYPES
    assert httpx.Client in CLIENT_TYPES
    assert httpx.AsyncClient in ASYNC_CLIENT_TYPES


def test_sends_requests_with_httpx2_client(fake_config: Configuration) -> None:
    """Test that requests go through a user-supplied httpx2 client."""
    http_client = httpx2.Client(transport=httpx2.MockTransport(_ok_response))
    api_call = ApiCall(fake_config, http_client)

    response = api_call.get("/", entity_type=typing.Dict[str, str])

    assert response == {"key": "value"}


async def test_async_sends_requests_with_httpx2_client(
    fake_config: Configuration,
) -> None:
    """Test that requests go through a user-supplied httpx2 async client."""
    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(_ok_response))
    api_call = AsyncApiCall(fake_config, http_client)

    response = await api_call.get("/", entity_type=typing.Dict[str, str])

    assert response == {"key": "value"}


def test_httpx2_connect_error_fails_over(fake_config: Configuration) -> None:
    """Test that an httpx2 connection error marks the node unhealthy and fails over."""

    def handler(request: typing.Any) -> typing.Any:
        if request.url.host == "nearest":
            raise httpx2.ConnectError("Connection refused", request=request)
        return httpx2.Response(200, json={"key": "value"})

    http_client = httpx2.Client(transport=httpx2.MockTransport(handler))
    api_call = ApiCall(fake_config, http_client)

    response = api_call.get("/", entity_type=typing.Dict[str, str])

    assert response == {"key": "value"}
    assert fake_config.nearest_node.healthy is False


def test_httpx2_client_side_error_does_not_fail_over(
    fake_config: Configuration,
) -> None:
    """Test that an httpx2 PoolTimeout propagates without marking the node unhealthy."""
    requested_hosts: typing.List[str] = []

    def handler(request: typing.Any) -> typing.Any:
        requested_hosts.append(request.url.host)
        raise httpx2.PoolTimeout("Pool timeout", request=request)

    http_client = httpx2.Client(transport=httpx2.MockTransport(handler))
    api_call = ApiCall(fake_config, http_client)

    with pytest.raises(httpx2.PoolTimeout):
        api_call.get("/", entity_type=typing.Dict[str, str])

    assert requested_hosts == ["nearest"]
    assert fake_config.nearest_node.healthy is True


def test_httpx2_server_error_response_fails_over(fake_config: Configuration) -> None:
    """Test that a 503 through an httpx2 client fails over to the next node."""

    def handler(request: typing.Any) -> typing.Any:
        if request.url.host == "nearest":
            return httpx2.Response(503, json={"message": "unavailable"})
        return httpx2.Response(200, json={"key": "value"})

    http_client = httpx2.Client(transport=httpx2.MockTransport(handler))
    api_call = ApiCall(fake_config, http_client)

    response = api_call.get("/", entity_type=typing.Dict[str, str])

    assert response == {"key": "value"}
    assert fake_config.nearest_node.healthy is False


def test_rejects_async_client_for_sync_api_call(fake_config: Configuration) -> None:
    """Test that the sync client refuses an async http client."""
    with pytest.raises(TypeError, match="`http_client` must be"):
        ApiCall(fake_config, typing.cast(typing.Any, httpx2.AsyncClient()))


def test_rejects_sync_client_for_async_api_call(fake_config: Configuration) -> None:
    """Test that the async client refuses a sync http client."""
    with pytest.raises(TypeError, match="`http_client` must be"):
        AsyncApiCall(fake_config, typing.cast(typing.Any, httpx2.Client()))


def test_close_leaves_user_supplied_client_open(fake_config: Configuration) -> None:
    """Test that closing the api call does not close a client the caller owns."""
    http_client = httpx2.Client(transport=httpx2.MockTransport(_ok_response))
    api_call = ApiCall(fake_config, http_client)

    api_call.close()

    assert http_client.is_closed is False


def test_close_closes_default_client(fake_config: Configuration) -> None:
    """Test that closing the api call closes the client it created."""
    api_call = ApiCall(fake_config)

    api_call.close()

    assert api_call._client.is_closed is True


async def test_async_close_leaves_user_supplied_client_open(
    fake_config: Configuration,
) -> None:
    """Test that closing the async api call does not close a caller-owned client."""
    http_client = httpx2.AsyncClient(transport=httpx2.MockTransport(_ok_response))
    api_call = AsyncApiCall(fake_config, http_client)

    await api_call.aclose()

    assert http_client.is_closed is False
    await http_client.aclose()
