"""Tests for the Metrics class."""


from tests.utils.object_assertions import (
    assert_match_object,
    assert_object_lists_match,
)
from typesense.sync.api_call import ApiCall
from typesense.async_.api_call import AsyncApiCall
from typesense.async_.metrics import AsyncMetrics
from typesense.sync.metrics import Metrics


def test_init(fake_api_call: ApiCall) -> None:
    """Test that the Metrics object is initialized correctly."""
    metrics = Metrics(fake_api_call)

    assert_match_object(metrics.api_call, fake_api_call)
    assert_object_lists_match(
        metrics.api_call.node_manager.nodes,
        fake_api_call.node_manager.nodes,
    )
    assert_match_object(
        metrics.api_call.config.nearest_node,
        fake_api_call.config.nearest_node,
    )
    assert metrics.resource_path == "/metrics.json"  # noqa: WPS437


def test_init_async(fake_async_api_call: AsyncApiCall) -> None:
    """Test that the AsyncMetrics object is initialized correctly."""
    metrics = AsyncMetrics(fake_async_api_call)

    assert_match_object(metrics.api_call, fake_async_api_call)
    assert_object_lists_match(
        metrics.api_call.node_manager.nodes,
        fake_async_api_call.node_manager.nodes,
    )
    assert_match_object(
        metrics.api_call.config.nearest_node,
        fake_async_api_call.config.nearest_node,
    )
    assert metrics.resource_path == "/metrics.json"  # noqa: WPS437

import platform


def test_actual_retrieve(actual_metrics: Metrics) -> None:
    """Test that the Metrics object can retrieve metrics on Typesense server and verify response structure."""
    response = actual_metrics.retrieve()

    if platform.system() == "Linux":
        assert "system_cpu_active_percentage" in response
        assert "system_network_received_bytes" in response
        assert "system_network_sent_bytes" in response

    assert "system_disk_total_bytes" in response
    assert "system_disk_used_bytes" in response
    assert "system_memory_total_bytes" in response
    assert "system_memory_used_bytes" in response
    assert "typesense_memory_active_bytes" in response
    assert "typesense_memory_allocated_bytes" in response
    assert "typesense_memory_fragmentation_ratio" in response

    assert "typesense_memory_mapped_bytes" in response
    assert "typesense_memory_metadata_bytes" in response
    assert "typesense_memory_resident_bytes" in response
    assert "typesense_memory_retained_bytes" in response


async def test_actual_retrieve_async(actual_async_metrics: AsyncMetrics) -> None:
    """Test that the AsyncMetrics object can retrieve metrics on Typesense server and verify response structure."""
    response = await actual_async_metrics.retrieve()

    if platform.system() == "Linux":
        assert "system_cpu_active_percentage" in response
        assert "system_network_received_bytes" in response
        assert "system_network_sent_bytes" in response

    assert "system_disk_total_bytes" in response
    assert "system_disk_used_bytes" in response
    assert "system_memory_total_bytes" in response
    assert "system_memory_used_bytes" in response
    assert "typesense_memory_active_bytes" in response
    assert "typesense_memory_allocated_bytes" in response
    assert "typesense_memory_fragmentation_ratio" in response

    assert "typesense_memory_mapped_bytes" in response
    assert "typesense_memory_metadata_bytes" in response
    assert "typesense_memory_resident_bytes" in response
    assert "typesense_memory_retained_bytes" in response
