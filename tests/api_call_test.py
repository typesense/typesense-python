"""Unit Tests for the ApiCall class."""

import time

import pytest
import requests
import requests_mock
from pytest_mock import MockerFixture

from tests.utils.object_assertions import assert_match_object, assert_object_lists_match
from typesense import exceptions
from typesense.api_call import ApiCall
from typesense.configuration import Configuration, Node


@pytest.fixture(scope="function", name="config")
def config_fixture() -> Configuration:
    """Return a Configuration object with test values."""
    return Configuration(
        config_dict={
            "api_key": "test-api-key",
            "nodes": [
                {
                    "host": "node0",
                    "port": 8108,
                    "protocol": "http",
                },
                {
                    "host": "node1",
                    "port": 8108,
                    "protocol": "http",
                },
                {
                    "host": "node2",
                    "port": 8108,
                    "protocol": "http",
                },
            ],
            "nearest_node": {
                "host": "nearest",
                "port": 8108,
                "protocol": "http",
            },
            "num_retries": 3,
            "healthcheck_interval_seconds": 60,
            "retry_interval_seconds": 0.001,
            "connection_timeout_seconds": 0.001,
            "verify": True,
        },
    )


@pytest.fixture(scope="function", name="api_call")
def api_call_fixture(
    config: Configuration,
) -> ApiCall[dict[str, str], dict[str, str], dict[str, str]]:
    """Return an ApiCall object with test values."""
    return ApiCall[dict[str, str], dict[str, str], dict[str, str]](config)


def test_initialization(
    api_call: ApiCall[dict[str, str], dict[str, str], dict[str, str]],
    config: Configuration,
) -> None:
    """Test the initialization of the ApiCall object."""
    assert api_call.config == config
    assert_object_lists_match(api_call.nodes, config.nodes)
    assert api_call.node_index == 0


def test_node_due_for_health_check(
    api_call: ApiCall[dict[str, str], dict[str, str], dict[str, str]],
) -> None:
    """Test that it correctly identifies if a node is due for health check."""
    node = Node(host="localhost", port=8108, protocol="http", path=" ")
    node.last_access_ts = time.time() - 61
    assert api_call.node_due_for_health_check(node) is True


def test_get_node_nearest_healthy(
    api_call: ApiCall[dict[str, str], dict[str, str], dict[str, str]],
) -> None:
    """Test that it correctly selects the nearest node if it is healthy."""
    node = api_call.get_node()
    assert_match_object(node, api_call.config.nearest_node)


def test_get_node_nearest_not_healthy(
    api_call: ApiCall[dict[str, str], dict[str, str], dict[str, str]],
) -> None:
    """Test that it selects the next available node if the nearest node is not healthy."""
    api_call.config.nearest_node.healthy = False
    node = api_call.get_node()
    assert_match_object(node, api_call.nodes[0])


def test_get_node_round_robin_selection(
    api_call: ApiCall[dict[str, str], dict[str, str], dict[str, str]],
    mocker: MockerFixture,
) -> None:
    """Test that it selects the next available node in a round-robin fashion."""
    api_call.config.nearest_node = None
    mocker.patch("time.time", return_value=100)

    node1 = api_call.get_node()
    assert_match_object(node1, api_call.config.nodes[0])

    node2 = api_call.get_node()
    assert_match_object(node2, api_call.config.nodes[1])

    node3 = api_call.get_node()
    assert_match_object(node3, api_call.config.nodes[2])


def test_get_exception() -> None:
    """Test that it correctly returns the exception class for a given status code."""
    assert ApiCall.get_exception(0) == exceptions.HTTPStatus0Error
    assert ApiCall.get_exception(400) == exceptions.RequestMalformed
    assert ApiCall.get_exception(401) == exceptions.RequestUnauthorized
    assert ApiCall.get_exception(403) == exceptions.RequestForbidden
    assert ApiCall.get_exception(404) == exceptions.ObjectNotFound
    assert ApiCall.get_exception(409) == exceptions.ObjectAlreadyExists
    assert ApiCall.get_exception(422) == exceptions.ObjectUnprocessable
    assert ApiCall.get_exception(500) == exceptions.ServerError
    assert ApiCall.get_exception(503) == exceptions.ServiceUnavailable
    assert ApiCall.get_exception(999) == exceptions.TypesenseClientError


def test_normalize_params_with_booleans() -> None:
    """Test that it correctly normalizes boolean values to strings."""
    parameter_dict: dict[str, str | bool] = {"key1": True, "key2": False}
    ApiCall.normalize_params(parameter_dict)

    assert parameter_dict == {"key1": "true", "key2": "false"}


def test_normalize_params_with_mixed_types() -> None:
    """Test that it correctly normalizes boolean values to strings."""
    parameter_dict = {"key1": True, "key2": False, "key3": "value", "key4": 123}
    ApiCall.normalize_params(parameter_dict)
    assert parameter_dict == {
        "key1": "true",
        "key2": "false",
        "key3": "value",
        "key4": 123,
    }


def test_normalize_params_with_empty_dict() -> None:
    """Test that it correctly normalizes an empty dictionary."""
    parameter_dict: dict[str, str] = {}
    ApiCall.normalize_params(parameter_dict)
    assert not parameter_dict


def test_normalize_params_with_no_booleans() -> None:
    """Test that it correctly normalizes a dictionary with no boolean values."""
    parameter_dict = {"key1": "value", "key2": 123}
    ApiCall.normalize_params(parameter_dict)
    assert parameter_dict == {"key1": "value", "key2": 123}


def test_make_request_as_json(api_call: ApiCall) -> None:
    """Test the `make_request` method with JSON response."""
    session = requests.sessions.Session()

    with requests_mock.mock(session=session) as request_mocker:
        request_mocker.get(
            "http://nearest:8108/test",
            json={"key": "value"},
            status_code=200,
        )

        response = api_call.make_request(session.get, "/test", as_json=True)
        assert response == {"key": "value"}


def test_make_request_as_text(api_call: ApiCall) -> None:
    """Test the `make_request` method with text response."""
    session = requests.sessions.Session()

    with requests_mock.mock(session=session) as request_mocker:
        request_mocker.get(
            "http://nearest:8108/test",
            text="response text",
            status_code=200,
        )

        response = api_call.make_request(session.get, "/test", as_json=False)
        assert response == "response text"


def test_get_as_json(
    api_call: ApiCall[dict[str, str], dict[str, str], dict[str, str]],
) -> None:
    """Test the GET method with JSON response."""
    with requests_mock.mock() as request_mocker:
        request_mocker.get(
            "http://nearest:8108/test",
            json={"key": "value"},
            status_code=200,
        )
        assert api_call.get("/test", as_json=True) == {"key": "value"}


def test_get_as_text(
    api_call: ApiCall[dict[str, str], dict[str, str], dict[str, str]],
) -> None:
    """Test the GET method with text response."""
    with requests_mock.mock() as request_mocker:
        request_mocker.get(
            "http://nearest:8108/test",
            text="response text",
            status_code=200,
        )
        assert api_call.get("/test", as_json=False) == "response text"


def test_post_as_json(
    api_call: ApiCall[dict[str, str], dict[str, str], dict[str, str]],
) -> None:
    """Test the POST method with JSON response."""
    with requests_mock.mock() as request_mocker:
        request_mocker.post(
            "http://nearest:8108/test",
            json={"key": "value"},
            status_code=200,
        )
        assert api_call.post("/test", body={"data": "value"}, as_json=True) == {
            "key": "value",
        }


def test_post_with_params(
    api_call: ApiCall[dict[str, str], dict[str, str], dict[str, str]],
) -> None:
    """Test that the parameters are correctly passed to the request."""
    with requests_mock.Mocker() as request_mocker:
        request_mocker.post(
            "http://nearest:8108/test",
            json={"key": "value"},
            status_code=200,
        )

        parameter_set = {"key1": [True, False], "key2": False, "key3": "value"}

        post_result = api_call.post(
            "/test",
            params=parameter_set,
            body={"key": "value"},
            as_json=True,
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
    api_call: ApiCall[dict[str, str], dict[str, str], dict[str, str]],
) -> None:
    """Test the POST method with text response."""
    with requests_mock.mock() as request_mocker:
        request_mocker.post(
            "http://nearest:8108/test",
            text="response text",
            status_code=200,
        )
        post_result = api_call.post("/test", body={"data": "value"}, as_json=False)
        assert post_result == "response text"


def test_put_as_json(
    api_call: ApiCall[dict[str, str], dict[str, str], dict[str, str]],
) -> None:
    """Test the PUT method with JSON response."""
    with requests_mock.mock() as request_mocker:
        request_mocker.put(
            "http://nearest:8108/test",
            json={"key": "value"},
            status_code=200,
        )
        assert api_call.put("/test", body={"data": "value"}) == {"key": "value"}


def test_patch_as_json(
    api_call: ApiCall[dict[str, str], dict[str, str], dict[str, str]],
) -> None:
    """Test the PATCH method with JSON response."""
    with requests_mock.mock() as request_mocker:
        request_mocker.patch(
            "http://nearest:8108/test",
            json={"key": "value"},
            status_code=200,
        )
        assert api_call.patch("/test", body={"data": "value"}) == {"key": "value"}


def test_delete_as_json(
    api_call: ApiCall[dict[str, str], dict[str, str], dict[str, str]],
) -> None:
    """Test the DELETE method with JSON response."""
    with requests_mock.mock() as request_mocker:
        request_mocker.delete(
            "http://nearest:8108/test",
            json={"key": "value"},
            status_code=200,
        )

        response = api_call.delete("/test")
        assert response == {"key": "value"}


def test_raise_custom_exception_with_header(
    api_call: ApiCall[dict[str, str], dict[str, str], dict[str, str]],
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
            api_call.make_request(requests.get, "/test", as_json=True)
            assert str(exception.value) == "[Errno 400] Test error"


def test_raise_custom_exception_without_header(
    api_call: ApiCall[dict[str, str], dict[str, str], dict[str, str]],
) -> None:
    """Test that it raises a custom exception with the error message."""
    with requests_mock.mock() as request_mocker:
        request_mocker.get(
            "http://nearest:8108/test",
            json={"message": "Test error"},
            status_code=400,
        )

        with pytest.raises(exceptions.RequestMalformed) as exception:
            api_call.make_request(requests.get, "/test", as_json=True)
            assert str(exception.value) == "[Errno 400] API error."


def test_selects_next_available_node_on_timeout(
    api_call: ApiCall[dict[str, str], dict[str, str], dict[str, str]],
) -> None:
    """Test that it selects the next available node if the request times out."""
    with requests_mock.mock() as request_mocker:
        api_call.config.nearest_node = None
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

        response = api_call.get("/test", as_json=True)

        assert response == {"key": "value"}
        assert request_mocker.request_history[0].url == "http://node0:8108/test"
        assert request_mocker.request_history[1].url == "http://node1:8108/test"
        assert request_mocker.request_history[2].url == "http://node2:8108/test"
        assert request_mocker.call_count == 3


def test_raises_if_no_nodes_are_healthy_with_the_last_exception(
    api_call: ApiCall[dict[str, str], dict[str, str], dict[str, str]],
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
            api_call.get("/")


def test_uses_nearest_node_if_present_and_healthy(
    mocker: MockerFixture,
    api_call: ApiCall[dict[str, str], dict[str, str], dict[str, str]],
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
        api_call.get("/")
        # 1 should go to node2 and resolve the request: 1 request
        api_call.get("/")
        # 1 should go to node2 and resolve the request: 1 request
        api_call.get("/")

        # Advance time by 5 seconds
        mocker.patch("time.time", return_value=current_time + 5)
        api_call.get("/")  # 1 should go to node2 and resolve the request: 1 request

        # Advance time by 65 seconds
        mocker.patch("time.time", return_value=current_time + 65)

        # 1 should go to nearest,
        # 2 should go to node0,
        # 3 should go to node1,
        # 4 should go to node2 and resolve the request: 4 requests
        api_call.get("/")

        # Advance time by 185 seconds
        mocker.patch("time.time", return_value=current_time + 185)

        # Resolve the request on the nearest node
        request_mocker.get(
            "http://nearest:8108/",
            json={"message": "Success"},
            status_code=200,
        )

        # 1 should go to nearest and resolve the request: 1 request
        api_call.get("/")
        # 1 should go to nearest and resolve the request: 1 request
        api_call.get("/")
        # 1 should go to nearest and resolve the request: 1 request
        api_call.get("/")

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
