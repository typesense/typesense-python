"""Unit Tests for the ApiCall class."""

import logging
import sys
import time

from pytest_mock import MockFixture

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

import httpx
import pytest
import respx
from pytest_mock import MockerFixture

from tests.utils.object_assertions import assert_match_object, assert_object_lists_match
from typesense import exceptions
from typesense.sync.api_call import ApiCall, RequestHandler
from typesense.async_.api_call import AsyncApiCall
from typesense.configuration import Configuration, Node
from typesense.logger import logger


def test_initialization(
    fake_config: Configuration,
) -> None:
    """Test the initialization of the ApiCall object."""
    fake_api_call = ApiCall(fake_config)
    assert fake_api_call.config == fake_config
    assert_object_lists_match(fake_api_call.node_manager.nodes, fake_config.nodes)
    assert fake_api_call.node_manager.node_index == 0


def test_node_due_for_health_check(
    fake_api_call: ApiCall,
) -> None:
    """Test that it correctly identifies if a node is due for health check."""
    node = Node(host="localhost", port=8108, protocol="http", path=" ")
    node.last_access_ts = time.time() - 61
    assert fake_api_call.node_manager._is_due_for_health_check(node) is True


def test_get_node_nearest_healthy(
    fake_api_call: ApiCall,
) -> None:
    """Test that it correctly selects the nearest node if it is healthy."""
    node = fake_api_call.node_manager.get_node()
    assert_match_object(node, fake_api_call.config.nearest_node)


def test_get_node_nearest_not_healthy(
    fake_api_call: ApiCall,
) -> None:
    """Test that it selects the next available node if the nearest node is not healthy."""
    fake_api_call.config.nearest_node.healthy = False
    node = fake_api_call.node_manager.get_node()
    assert_match_object(node, fake_api_call.node_manager.nodes[0])


def test_get_node_round_robin_selection(
    fake_api_call: ApiCall,
    mocker: MockerFixture,
) -> None:
    """Test that it selects the next available node in a round-robin fashion."""
    fake_api_call.config.nearest_node = None
    mocker.patch("time.time", return_value=100)

    node1 = fake_api_call.node_manager.get_node()
    assert_match_object(node1, fake_api_call.config.nodes[0])

    node2 = fake_api_call.node_manager.get_node()
    assert_match_object(node2, fake_api_call.config.nodes[1])

    node3 = fake_api_call.node_manager.get_node()
    assert_match_object(node3, fake_api_call.config.nodes[2])


def test_get_exception() -> None:
    """Test that it correctly returns the exception class for a given status code."""
    assert RequestHandler._get_exception(0) == exceptions.HTTPStatus0Error
    assert RequestHandler._get_exception(400) == exceptions.RequestMalformed
    assert RequestHandler._get_exception(401) == exceptions.RequestUnauthorized
    assert RequestHandler._get_exception(403) == exceptions.RequestForbidden
    assert RequestHandler._get_exception(404) == exceptions.ObjectNotFound
    assert RequestHandler._get_exception(409) == exceptions.ObjectAlreadyExists
    assert RequestHandler._get_exception(422) == exceptions.ObjectUnprocessable
    assert RequestHandler._get_exception(500) == exceptions.ServerError
    assert RequestHandler._get_exception(503) == exceptions.ServiceUnavailable
    assert RequestHandler._get_exception(999) == exceptions.TypesenseClientError


def test_get_error_message_with_invalid_json() -> None:
    """Test that it correctly handles invalid JSON in error responses."""
    response = httpx.Response(
        400,
        headers={"Content-Type": "application/json"},
        content=b'{"message": "Error occurred", "details": {"key": "value"',
    )

    error_message = RequestHandler._get_error_message(response)
    assert "API error: Invalid JSON response:" in error_message
    assert '{"message": "Error occurred", "details": {"key": "value"' in error_message


def test_get_error_message_with_valid_json() -> None:
    """Test that it correctly extracts error message from valid JSON responses."""
    response = httpx.Response(
        400,
        headers={"Content-Type": "application/json"},
        content=b'{"message": "Error occurred", "details": {"key": "value"}}',
    )

    error_message = RequestHandler._get_error_message(response)
    assert error_message == "Error occurred"


def test_get_error_message_with_non_json_content_type() -> None:
    """Test that it returns a default error message for non-JSON content types."""
    response = httpx.Response(
        400,
        headers={"Content-Type": "text/plain"},
        content=b"Not a JSON content",
    )

    error_message = RequestHandler._get_error_message(response)
    assert error_message == "API error. Not a JSON content"


def test_normalize_params_with_booleans() -> None:
    """Test that it correctly normalizes boolean values to strings."""
    parameter_dict: typing.Dict[str, str | bool] = {"key1": True, "key2": False}
    RequestHandler.normalize_params(parameter_dict)

    assert parameter_dict == {"key1": "true", "key2": "false"}


def test_normalize_params_with_non_dict() -> None:
    """Test that it raises when a non-dictionary is passed."""
    parameter_non_dict = "string"

    with pytest.raises(ValueError):
        RequestHandler.normalize_params(parameter_non_dict)


def test_normalize_params_with_mixed_types() -> None:
    """Test that it correctly normalizes boolean values to strings."""
    parameter_dict = {"key1": True, "key2": False, "key3": "value", "key4": 123}
    RequestHandler.normalize_params(parameter_dict)
    assert parameter_dict == {
        "key1": "true",
        "key2": "false",
        "key3": "value",
        "key4": 123,
    }


def test_normalize_params_with_empty_dict() -> None:
    """Test that it correctly normalizes an empty dictionary."""
    parameter_dict: typing.Dict[str, str] = {}
    RequestHandler.normalize_params(parameter_dict)
    assert not parameter_dict


def test_normalize_params_with_no_booleans() -> None:
    """Test that it correctly normalizes a dictionary with no boolean values."""
    parameter_dict = {"key1": "value", "key2": 123}
    RequestHandler.normalize_params(parameter_dict)
    assert parameter_dict == {"key1": "value", "key2": 123}


def test_additional_headers(fake_api_call: ApiCall) -> None:
    """Test the `make_request` method with additional headers from the config."""
    api_call = ApiCall(
        Configuration(
            {
                "additional_headers": {
                    "AdditionalHeader1": "test",
                    "AdditionalHeader2": "test2",
                },
                "api_key": "test-api",
                "nodes": [
                    "http://nearest:8108",
                ],
            },
        ),
    )

    with respx.mock:
        respx.get("http://nearest:8108/test").mock(
            return_value=httpx.Response(200, json={"key": "value"})
        )

        api_call._execute_request(
            "GET",
            "/test",
            as_json=True,
            entity_type=typing.Dict[str, str],
        )

        request = respx.calls.last.request
        assert request.headers["AdditionalHeader1"] == "test"
        assert request.headers["AdditionalHeader2"] == "test2"


def test_make_request_as_json(fake_api_call: ApiCall) -> None:
    """Test the `make_request` method with JSON response."""
    with respx.mock:
        respx.get("http://nearest:8108/test").mock(
            return_value=httpx.Response(200, json={"key": "value"})
        )

        response = fake_api_call._execute_request(
            "GET",
            "/test",
            as_json=True,
            entity_type=typing.Dict[str, str],
        )
        assert response == {"key": "value"}


def test_make_request_as_text(fake_api_call: ApiCall) -> None:
    """Test the `make_request` method with text response."""
    with respx.mock:
        respx.get("http://nearest:8108/test").mock(
            return_value=httpx.Response(200, text="response text")
        )

        response = fake_api_call._execute_request(
            "GET",
            "/test",
            as_json=False,
            entity_type=typing.Dict[str, str],
        )

        assert response == "response text"


def test_get_as_json(
    fake_api_call: ApiCall,
) -> None:
    """Test the GET method with JSON response."""
    with respx.mock:
        respx.get("http://nearest:8108/test").mock(
            return_value=httpx.Response(200, json={"key": "value"})
        )
        assert fake_api_call.get(
            "/test",
            as_json=True,
            entity_type=typing.Dict[str, str],
        ) == {"key": "value"}


def test_get_as_text(
    fake_api_call: ApiCall,
) -> None:
    """Test the GET method with text response."""
    with respx.mock:
        respx.get("http://nearest:8108/test").mock(
            return_value=httpx.Response(200, text="response text")
        )
        assert (
            fake_api_call.get("/test", as_json=False, entity_type=typing.Dict[str, str])
            == "response text"
        )


def test_post_as_json(
    fake_api_call: ApiCall,
) -> None:
    """Test the POST method with JSON response."""
    with respx.mock:
        respx.post("http://nearest:8108/test").mock(
            return_value=httpx.Response(200, json={"key": "value"})
        )
        assert fake_api_call.post(
            "/test",
            body={"data": "value"},
            as_json=True,
            entity_type=typing.Dict[str, str],
        ) == {
            "key": "value",
        }


def test_post_with_params(
    fake_api_call: ApiCall,
) -> None:
    """Test that the parameters are correctly passed to the request."""
    with respx.mock:
        route = respx.post("http://nearest:8108/test").mock(
            return_value=httpx.Response(200, json={"key": "value"})
        )

        parameter_set = {"key1": [True, False], "key2": False, "key3": "value"}

        post_result = fake_api_call.post(
            "/test",
            params=parameter_set,
            body={"key": "value"},
            as_json=True,
            entity_type=typing.Dict[str, str],
        )

        expected_parameter_set = {
            "key1": ["true", "false"],
            "key2": ["false"],
            "key3": ["value"],
        }

        request = route.calls.last.request
        # respx stores params as a MultiDict, convert to dict for comparison
        params_dict: typing.Dict[str, typing.List[str]] = {}
        for key, value in request.url.params.multi_items():
            if key in params_dict:
                params_dict[key].append(value)
            else:
                params_dict[key] = [value]
        assert params_dict == expected_parameter_set
        assert post_result == {"key": "value"}


def test_post_as_text(
    fake_api_call: ApiCall,
) -> None:
    """Test the POST method with text response."""
    with respx.mock:
        respx.post("http://nearest:8108/test").mock(
            return_value=httpx.Response(200, text="response text")
        )
        post_result = fake_api_call.post(
            "/test",
            body={"data": "value"},
            as_json=False,
            entity_type=typing.Dict[str, str],
        )
        assert post_result == "response text"


def test_put_as_json(
    fake_api_call: ApiCall,
) -> None:
    """Test the PUT method with JSON response."""
    with respx.mock:
        respx.put("http://nearest:8108/test").mock(
            return_value=httpx.Response(200, json={"key": "value"})
        )
        assert fake_api_call.put(
            "/test",
            body={"data": "value"},
            entity_type=typing.Dict[str, str],
        ) == {"key": "value"}


def test_patch_as_json(
    fake_api_call: ApiCall,
) -> None:
    """Test the PATCH method with JSON response."""
    with respx.mock:
        respx.patch("http://nearest:8108/test").mock(
            return_value=httpx.Response(200, json={"key": "value"})
        )
        assert fake_api_call.patch(
            "/test",
            body={"data": "value"},
            entity_type=typing.Dict[str, str],
        ) == {"key": "value"}


def test_delete_as_json(
    fake_api_call: ApiCall,
) -> None:
    """Test the DELETE method with JSON response."""
    with respx.mock:
        respx.delete("http://nearest:8108/test").mock(
            return_value=httpx.Response(200, json={"key": "value"})
        )

        response = fake_api_call.delete("/test", entity_type=typing.Dict[str, str])
        assert response == {"key": "value"}


def test_raise_custom_exception_with_header(
    fake_api_call: ApiCall,
) -> None:
    """Test that it raises a custom exception with the error message."""
    with respx.mock:
        respx.get("http://nearest:8108/test").mock(
            return_value=httpx.Response(
                400,
                json={"message": "Test error"},
                headers={"Content-Type": "application/json"},
            )
        )

        with pytest.raises(exceptions.RequestMalformed) as exception:
            fake_api_call._execute_request(
                "GET",
                "/test",
                as_json=True,
                entity_type=typing.Dict[str, str],
            )
        assert str(exception.value) == "[Errno 400] Test error"


def test_raise_custom_exception_without_header(
    fake_api_call: ApiCall,
) -> None:
    """Test that it raises a custom exception with the error message."""
    with respx.mock:
        # Use content instead of json to avoid automatic Content-Type header
        # This tests the case where Content-Type is not application/json
        respx.get("http://nearest:8108/test").mock(
            return_value=httpx.Response(
                400,
                content=b'{"message": "Test error"}',
                headers={"Content-Type": "text/plain"},
            )
        )

        with pytest.raises(exceptions.RequestMalformed) as exception:
            fake_api_call._execute_request(
                "GET",
                "/test",
                as_json=True,
                entity_type=typing.Dict[str, str],
            )
        assert (
            str(exception.value) == '[Errno 400] API error. {"message": "Test error"}'
        )


def test_selects_next_available_node_on_timeout(
    fake_api_call: ApiCall,
) -> None:
    """Test that it selects the next available node if the request times out."""
    with respx.mock:
        fake_api_call.config.nearest_node = None
        respx.get("http://node0:8108/test").mock(
            side_effect=httpx.ConnectTimeout("Timeout")
        )
        respx.get("http://node1:8108/test").mock(
            side_effect=httpx.ConnectTimeout("Timeout")
        )
        respx.get("http://node2:8108/test").mock(
            return_value=httpx.Response(200, json={"key": "value"})
        )

        response = fake_api_call.get(
            "/test",
            as_json=True,
            entity_type=typing.Dict[str, str],
        )

        assert response == {"key": "value"}
        assert respx.calls[0].request.url == "http://node0:8108/test"
        assert respx.calls[1].request.url == "http://node1:8108/test"
        assert respx.calls[2].request.url == "http://node2:8108/test"
        assert len(respx.calls) == 3


def test_get_node_no_healthy_nodes(
    fake_api_call: ApiCall,
    mocker: MockFixture,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that it logs a message if no healthy nodes are found."""
    for api_node in fake_api_call.node_manager.nodes:
        api_node.healthy = False

    fake_api_call.config.nearest_node.healthy = False

    mocker.patch.object(
        fake_api_call.node_manager,
        "_is_due_for_health_check",
        return_value=False,
    )

    # Need to set the logger level to DEBUG to capture the message
    logger.setLevel(logging.DEBUG)

    selected_node = fake_api_call.node_manager.get_node()

    with caplog.at_level(logging.DEBUG):
        assert "No healthy nodes were found. Returning the next node." in caplog.text

    assert (
        selected_node
        == fake_api_call.node_manager.nodes[fake_api_call.node_manager.node_index]
    )

    assert fake_api_call.node_manager.node_index == 0


def test_raises_if_no_nodes_are_healthy_with_the_last_exception(
    fake_api_call: ApiCall,
) -> None:
    """Test that it raises the last exception if no nodes are healthy."""
    with respx.mock:
        respx.get("http://nearest:8108/").mock(
            side_effect=httpx.ConnectTimeout("Timeout")
        )
        respx.get("http://node0:8108/").mock(
            side_effect=httpx.ConnectTimeout("Timeout")
        )
        respx.get("http://node1:8108/").mock(
            side_effect=httpx.ConnectTimeout("Timeout")
        )
        respx.get("http://node2:8108/").mock(
            side_effect=httpx.ConnectError("SSL Error")
        )

        with pytest.raises(httpx.ConnectError):
            fake_api_call.get("/", entity_type=typing.Dict[str, str])


def test_uses_nearest_node_if_present_and_healthy(  # noqa: WPS213
    mocker: MockerFixture,
    fake_api_call: ApiCall,
) -> None:
    """Test that it uses the nearest node if it is present and healthy."""
    with respx.mock:
        nearest_route = respx.get("http://nearest:8108/")
        nearest_route.mock(side_effect=httpx.ConnectTimeout("Timeout"))
        respx.get("http://node0:8108/").mock(
            side_effect=httpx.ConnectTimeout("Timeout")
        )
        respx.get("http://node1:8108/").mock(
            side_effect=httpx.ConnectTimeout("Timeout")
        )
        respx.get("http://node2:8108/").mock(
            return_value=httpx.Response(200, json={"message": "Success"})
        )

        # Freeze time
        current_time = time.time()
        mocker.patch("time.time", return_value=current_time)

        # Perform the requests

        # 1 should go to nearest,
        # 2 should go to node0,
        # 3 should go to node1,
        # 4 should go to node2 and resolve the request: 4 requests
        fake_api_call.get("/", entity_type=typing.Dict[str, str])
        # 1 should go to node2 and resolve the request: 1 request
        fake_api_call.get("/", entity_type=typing.Dict[str, str])
        # 1 should go to node2 and resolve the request: 1 request
        fake_api_call.get("/", entity_type=typing.Dict[str, str])

        # Advance time by 5 seconds
        mocker.patch("time.time", return_value=current_time + 5)
        fake_api_call.get(
            "/",
            entity_type=typing.Dict[str, str],
        )  # 1 should go to node2 and resolve the request: 1 request

        # Advance time by 65 seconds
        mocker.patch("time.time", return_value=current_time + 65)

        # 1 should go to nearest,
        # 2 should go to node0,
        # 3 should go to node1,
        # 4 should go to node2 and resolve the request: 4 requests
        fake_api_call.get("/", entity_type=typing.Dict[str, str])

        # Advance time by 185 seconds
        mocker.patch("time.time", return_value=current_time + 185)

        # Resolve the request on the nearest node
        nearest_route.mock(
            return_value=httpx.Response(200, json={"message": "Success"})
        )

        # 1 should go to nearest and resolve the request: 1 request
        fake_api_call.get("/", entity_type=typing.Dict[str, str])
        # 1 should go to nearest and resolve the request: 1 request
        fake_api_call.get("/", entity_type=typing.Dict[str, str])
        # 1 should go to nearest and resolve the request: 1 request
        fake_api_call.get("/", entity_type=typing.Dict[str, str])

        # Check the request history
        assert str(respx.calls[0].request.url) == "http://nearest:8108/"
        assert str(respx.calls[1].request.url) == "http://node0:8108/"
        assert str(respx.calls[2].request.url) == "http://node1:8108/"
        assert str(respx.calls[3].request.url) == "http://node2:8108/"

        assert str(respx.calls[4].request.url) == "http://node2:8108/"
        assert str(respx.calls[5].request.url) == "http://node2:8108/"

        assert str(respx.calls[6].request.url) == "http://node2:8108/"

        assert str(respx.calls[7].request.url) == "http://nearest:8108/"
        assert str(respx.calls[8].request.url) == "http://node0:8108/"
        assert str(respx.calls[9].request.url) == "http://node1:8108/"
        assert str(respx.calls[10].request.url) == "http://node2:8108/"

        assert str(respx.calls[11].request.url) == "http://nearest:8108/"
        assert str(respx.calls[12].request.url) == "http://nearest:8108/"
        assert str(respx.calls[13].request.url) == "http://nearest:8108/"


def test_max_retries_no_last_exception(fake_api_call: ApiCall) -> None:
    """Test that it raises if the maximum number of retries is reached."""
    with pytest.raises(
        exceptions.TypesenseClientError,
        match="All nodes are unhealthy",
    ):
        fake_api_call._execute_request(
            "GET",
            "/",
            as_json=True,
            entity_type=typing.Dict[str, str],
            num_retries=10,
            last_exception=None,
        )


def test_sleeps_retry_interval_between_retries(
    fake_api_call: ApiCall,
    mocker: MockerFixture,
) -> None:
    """Test that it waits ``retry_interval_seconds`` between failed attempts."""
    sleep_mock = mocker.patch("typesense.sync.api_call.time.sleep")

    with respx.mock:
        for host in ("nearest", "node0", "node1", "node2"):
            respx.get(f"http://{host}:8108/").mock(
                return_value=httpx.Response(503, json={"message": "unavailable"}),
            )

        with pytest.raises(exceptions.ServiceUnavailable):
            fake_api_call.get("/", entity_type=typing.Dict[str, str])

    # ``num_retries`` gaps for ``num_retries + 1`` attempts, and each gap must be
    # ``retry_interval_seconds`` long (regression: the delay was dropped entirely).
    assert sleep_mock.call_count == fake_api_call.config.num_retries
    for sleep_call in sleep_mock.call_args_list:
        assert sleep_call == mocker.call(fake_api_call.config.retry_interval_seconds)


async def test_async_sleeps_retry_interval_between_retries(
    fake_async_api_call: AsyncApiCall,
    mocker: MockerFixture,
) -> None:
    """Test that the async client waits ``retry_interval_seconds`` between attempts."""
    sleep_mock = mocker.patch(
        "typesense.async_.api_call.asyncio.sleep",
        new_callable=mocker.AsyncMock,
    )

    with respx.mock:
        for host in ("nearest", "node0", "node1", "node2"):
            respx.get(f"http://{host}:8108/").mock(
                return_value=httpx.Response(503, json={"message": "unavailable"}),
            )

        with pytest.raises(exceptions.ServiceUnavailable):
            await fake_async_api_call.get("/", entity_type=typing.Dict[str, str])

    assert sleep_mock.call_count == fake_async_api_call.config.num_retries
    for sleep_call in sleep_mock.call_args_list:
        assert sleep_call == mocker.call(
            fake_async_api_call.config.retry_interval_seconds,
        )
