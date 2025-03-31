"""Tests for the Debug class."""

from __future__ import annotations

from typesense.metrics import Metrics


def test_actual_retrieve(actual_metrics: Metrics) -> None:
    """Test that the Debug object can retrieve a debug on Typesense server and verify response structure."""
    response = actual_metrics.retrieve()

    assert "system_cpu_active_percentage" in response
    assert "system_disk_total_bytes" in response
    assert "system_disk_used_bytes" in response
    assert "system_memory_total_bytes" in response
    assert "system_memory_used_bytes" in response
    assert "system_network_received_bytes" in response
    assert "system_network_sent_bytes" in response
    assert "typesense_memory_active_bytes" in response
    assert "typesense_memory_allocated_bytes" in response
    assert "typesense_memory_fragmentation_ratio" in response

    assert "typesense_memory_mapped_bytes" in response
    assert "typesense_memory_metadata_bytes" in response
    assert "typesense_memory_resident_bytes" in response
    assert "typesense_memory_retained_bytes" in response