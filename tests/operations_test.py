"""Tests for the Operations class."""

from __future__ import annotations

import pytest
import requests_mock

from tests.utils.object_assertions import assert_match_object, assert_object_lists_match
from typesense.api_call import ApiCall
from typesense.exceptions import ObjectNotFound
from typesense.operations import Operations


def test_init(fake_api_call: ApiCall) -> None:
    """Test that the Override object is initialized correctly."""
    operations = Operations(fake_api_call)

    assert_match_object(operations.api_call, fake_api_call)
    assert_object_lists_match(
        operations.api_call.node_manager.nodes,
        fake_api_call.node_manager.nodes,
    )
    assert_match_object(
        operations.api_call.config.nearest_node,
        fake_api_call.config.nearest_node,
    )
    assert (
        operations._endpoint_path("resource") == "/operations/resource"  # noqa: WPS437
    )


def test_vote(actual_operations: Operations) -> None:
    """Test that the Operations object can perform the vote operation."""
    response = actual_operations.perform("vote")

    # It will error on single node clusters if asserted to True
    assert response["success"] is not None


def test_db_compact(actual_operations: Operations) -> None:
    """Test that the Operations object can perform the db/compact operation."""
    response = actual_operations.perform("db/compact")

    assert response["success"]


def test_cache_clear(actual_operations: Operations) -> None:
    """Test that the Operations object can perform the cache/clear operation."""
    response = actual_operations.perform("cache/clear")

    assert response["success"]


def test_snapshot(actual_operations: Operations) -> None:
    """Test that the Operations object can perform the snapshot operation."""
    response = actual_operations.perform(
        "snapshot",
        {"snapshot_path": "/tmp"},  # noqa: S108
    )

    assert response["success"]


def test_health(actual_operations: Operations) -> None:
    """Test that the Operations object can perform the health operation."""
    response = actual_operations.is_healthy()

    assert response


def test_health_not_dict(fake_operations: Operations) -> None:
    """Test that the Operations object can perform the health operation."""
    with requests_mock.Mocker() as mock:
        mock.get(
            "/health",
            json="ok",
        )

        response = fake_operations.is_healthy()
        assert not response


def test_log_slow_requests_time_ms(actual_operations: Operations) -> None:
    """Test that the Operations object can perform the log_slow_requests_time_ms operation."""
    response = actual_operations.toggle_slow_request_log(
        {"log_slow_requests_time_ms": 100},
    )

    assert response["success"]


def test_invalid_operation(actual_operations: Operations) -> None:
    """Test that the Operations object throws an error for an invalid operation."""
    with pytest.raises(ObjectNotFound):
        actual_operations.perform("invalid")
