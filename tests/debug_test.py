"""Tests for the Debug class."""

from __future__ import annotations

import requests_mock

from tests.utils.object_assertions import assert_match_object, assert_object_lists_match
from typesense.api_call import ApiCall
from typesense.debug import Debug
from typesense.types.debug import DebugResponseSchema


def test_init(fake_api_call: ApiCall) -> None:
    """Test that the Debug object is initialized correctly."""
    debug = Debug(
        fake_api_call,
    )

    assert_match_object(debug.api_call, fake_api_call)
    assert_object_lists_match(
        debug.api_call.node_manager.nodes,
        fake_api_call.node_manager.nodes,
    )
    assert_match_object(
        debug.api_call.config.nearest_node,
        fake_api_call.config.nearest_node,
    )
    assert debug.resource_path == "/debug"  # noqa: WPS437


def test_retrieve(fake_debug: Debug) -> None:
    """Test that the Debug object can retrieve a debug."""
    json_response: DebugResponseSchema = {"state": 1, "version": "27.1"}

    with requests_mock.Mocker() as mock:
        mock.get(
            "/debug",
            json=json_response,
        )

        response = fake_debug.retrieve()

        assert len(mock.request_history) == 1
        assert mock.request_history[0].method == "GET"
        assert mock.request_history[0].url == "http://nearest:8108/debug"
        assert response == json_response


def test_actual_retrieve(actual_debug: Debug) -> None:
    """Test that the Debug object can retrieve a debug on Typesense server."""
    json_response: DebugResponseSchema = {"state": 1, "version": "27.1"}

    response = actual_debug.retrieve()

    assert response == json_response
