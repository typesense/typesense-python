"""Unit Tests for the ApiCall class."""

from __future__ import annotations

import logging
import sys
import time

from isort import Config
from pytest_mock import MockFixture

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

import pytest
import requests
import requests_mock
from pytest_mock import MockerFixture

from tests.utils.object_assertions import assert_match_object, assert_object_lists_match
from typesense import exceptions
from typesense.api_call import ApiCall, RequestHandler
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
    session = requests.sessions.Session()
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

    with requests_mock.mock(session=session) as request_mocker:
        request_mocker.get(
            "http://nearest:8108/test",
            json={"key": "value"},
            status_code=200,
        )

        api_call._execute_request(
            session.get,
            "/test",
            as_json=True,
            entity_type=typing.Dict[str, str],
        )

        request = request_mocker.request_history[-1]
        assert request.headers["AdditionalHeader1"] == "test"
        assert request.headers["AdditionalHeader2"] == "test2"


def test_make_request_as_json(fake_api_call: ApiCall) -> None:
    """Test the `make_request` method with JSON response."""
    session = requests.sessions.Session()

    with requests_mock.mock(session=session) as request_mocker:
        request_mocker.get(
            "http://nearest:8108/test",
            json={"key": "value"},
            status_code=200,
        )

        response = fake_api_call._execute_request(
            session.get,
            "/test",
            as_json=True,
            entity_type=typing.Dict[str, str],
        )
        assert response == {"key": "value"}


def test_make_request_as_text(fake_api_call: ApiCall) -> None:
    """Test the `make_request` method with text response."""
    session = requests.sessions.Session()

    with requests_mock.mock(session=session) as request_mocker:
        request_mocker.get(
            "http://nearest:8108/test",
            text="response text",
            status_code=200,
        )

        response = fake_api_call._execute_request(
            session.get,
            "/test",
            as_json=False,
            entity_type=typing.Dict[str, str],
        )

        assert response == "response text"


def test_get_as_json(
    fake_api_call: ApiCall,
) -> None:
    """Test the GET method with JSON response."""
    with requests_mock.mock() as request_mocker:
        request_mocker.get(
            "http://nearest:8108/test",
            json={"key": "value"},
            status_code=200,
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
    with requests_mock.mock() as request_mocker:
        request_mocker.get(
            "http://nearest:8108/test",
            text="response text",
            status_code=200,
        )
        assert (
            fake_api_call.get("/test", as_json=False, entity_type=typing.Dict[str, str])
            == "response text"
        )


def test_post_as_json(
    fake_api_call: ApiCall,
) -> None:
    """Test the POST method with JSON response."""
    with requests_mock.mock() as request_mocker:
        request_mocker.post(
            "http://nearest:8108/test",
            json={"key": "value"},
            status_code=200,
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
    with requests_mock.Mocker() as request_mocker:
        request_mocker.post(
            "http://nearest:8108/test",
            json={"key": "value"},
            status_code=200,
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

        request = request_mocker.request_history[0]

        assert request.qs == expected_parameter_set
        assert post_result == {"key": "value"}


def test_post_as_text(
    fake_api_call: ApiCall,
) -> None:
    """Test the POST method with text response."""
    with requests_mock.mock() as request_mocker:
        request_mocker.post(
            "http://nearest:8108/test",
            text="response text",
            status_code=200,
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
    with requests_mock.mock() as request_mocker:
        request_mocker.put(
            "http://nearest:8108/test",
            json={"key": "value"},
            status_code=200,
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
    with requests_mock.mock() as request_mocker:
        request_mocker.patch(
            "http://nearest:8108/test",
            json={"key": "value"},
            status_code=200,
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
    with requests_mock.mock() as request_mocker:
        request_mocker.delete(
            "http://nearest:8108/test",
            json={"key": "value"},
            status_code=200,
        )

        response = fake_api_call.delete("/test", entity_type=typing.Dict[str, str])
        assert response == {"key": "value"}


def test_raise_custom_exception_with_header(
    fake_api_call: ApiCall,
) -> None:
    """Test that it raises a custom exception with the error message."""
    with requests_mock.mock() as request_mocker:
        request_mocker.get(
            "http://nearest:8108/test",
            json={"message": "Test error"},
            status_code=400,
            headers={"Content-Type": "application/json"},
        )

        with pytest.raises(exceptions.RequestMalformed) as exception:
            fake_api_call._execute_request(
                requests.get,
                "/test",
                as_json=True,
                entity_type=typing.Dict[str, str],
            )
            assert str(exception.value) == "[Errno 400] Test error"


def test_raise_custom_exception_without_header(
    fake_api_call: ApiCall,
) -> None:
    """Test that it raises a custom exception with the error message."""
    with requests_mock.mock() as request_mocker:
        request_mocker.get(
            "http://nearest:8108/test",
            json={"message": "Test error"},
            status_code=400,
        )

        with pytest.raises(exceptions.RequestMalformed) as exception:
            fake_api_call._execute_request(
                requests.get,
                "/test",
                as_json=True,
                entity_type=typing.Dict[str, str],
            )
            assert str(exception.value) == "[Errno 400] API error."


def test_selects_next_available_node_on_timeout(
    fake_api_call: ApiCall,
) -> None:
    """Test that it selects the next available node if the request times out."""
    with requests_mock.mock() as request_mocker:
        fake_api_call.config.nearest_node = None
        request_mocker.get(
            "http://node0:8108/test",
            exc=requests.exceptions.ConnectTimeout,
        )
        request_mocker.get(
            "http://node1:8108/test",
            exc=requests.exceptions.ConnectTimeout,
        )
        request_mocker.get(
            "http://node2:8108/test",
            json={"key": "value"},
            status_code=200,
        )

        response = fake_api_call.get(
            "/test",
            as_json=True,
            entity_type=typing.Dict[str, str],
        )

        assert response == {"key": "value"}
        assert request_mocker.request_history[0].url == "http://node0:8108/test"
        assert request_mocker.request_history[1].url == "http://node1:8108/test"
        assert request_mocker.request_history[2].url == "http://node2:8108/test"
        assert request_mocker.call_count == 3


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
    with requests_mock.mock() as request_mocker:
        request_mocker.get(
            "http://nearest:8108/",
            exc=requests.exceptions.ConnectTimeout,
        )
        request_mocker.get("http://node0:8108/", exc=requests.exceptions.ConnectTimeout)
        request_mocker.get("http://node1:8108/", exc=requests.exceptions.ConnectTimeout)
        request_mocker.get("http://node2:8108/", exc=requests.exceptions.SSLError)

        with pytest.raises(requests.exceptions.SSLError):
            fake_api_call.get("/", entity_type=typing.Dict[str, str])


def test_uses_nearest_node_if_present_and_healthy(  # noqa: WPS213
    mocker: MockerFixture,
    fake_api_call: ApiCall,
) -> None:
    """Test that it uses the nearest node if it is present and healthy."""
    with requests_mock.Mocker() as request_mocker:
        request_mocker.get(
            "http://nearest:8108/",
            exc=requests.exceptions.ConnectTimeout,
        )
        request_mocker.get("http://node0:8108/", exc=requests.exceptions.ConnectTimeout)
        request_mocker.get("http://node1:8108/", exc=requests.exceptions.ConnectTimeout)
        request_mocker.get(
            "http://node2:8108/",
            json={"message": "Success"},
            status_code=200,
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
        request_mocker.get(
            "http://nearest:8108/",
            json={"message": "Success"},
            status_code=200,
        )

        # 1 should go to nearest and resolve the request: 1 request
        fake_api_call.get("/", entity_type=typing.Dict[str, str])
        # 1 should go to nearest and resolve the request: 1 request
        fake_api_call.get("/", entity_type=typing.Dict[str, str])
        # 1 should go to nearest and resolve the request: 1 request
        fake_api_call.get("/", entity_type=typing.Dict[str, str])

        # Check the request history
        assert request_mocker.request_history[0].url == "http://nearest:8108/"
        assert request_mocker.request_history[1].url == "http://node0:8108/"
        assert request_mocker.request_history[2].url == "http://node1:8108/"
        assert request_mocker.request_history[3].url == "http://node2:8108/"

        assert request_mocker.request_history[4].url == "http://node2:8108/"
        assert request_mocker.request_history[5].url == "http://node2:8108/"

        assert request_mocker.request_history[6].url == "http://node2:8108/"

        assert request_mocker.request_history[7].url == "http://nearest:8108/"
        assert request_mocker.request_history[8].url == "http://node0:8108/"
        assert request_mocker.request_history[9].url == "http://node1:8108/"
        assert request_mocker.request_history[10].url == "http://node2:8108/"

        assert request_mocker.request_history[11].url == "http://nearest:8108/"
        assert request_mocker.request_history[12].url == "http://nearest:8108/"
        assert request_mocker.request_history[13].url == "http://nearest:8108/"


def test_max_retries_no_last_exception(fake_api_call: ApiCall) -> None:
    """Test that it raises if the maximum number of retries is reached."""
    with pytest.raises(
        exceptions.TypesenseClientError,
        match="All nodes are unhealthy",
    ):
        fake_api_call._execute_request(
            requests.get,
            "/",
            as_json=True,
            entity_type=typing.Dict[str, str],
            num_retries=10,
            last_exception=None,
        )
