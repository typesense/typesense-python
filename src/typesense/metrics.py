"""
This module provides functionality for retrieving metrics from the Typesense API.

It contains the Metrics class, which handles API operations for retrieving
system and Typesense metrics such as CPU, memory, disk, and network usage.

Classes:
    MetricsResponse: Type definition for metrics response.
    Metrics: Manages retrieving metrics from the Typesense API.

Dependencies:
    - typesense.api_call: Provides the ApiCall class for making API requests.

Note: This module uses conditional imports to support both Python 3.11+ and earlier versions.
"""

import sys

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

from typesense.api_call import ApiCall


class MetricsResponseBase(typing.TypedDict):
    """
    Response schema for metrics retrieval.

    This TypedDict includes system metrics like CPU, memory, disk, and network usage,
    as well as Typesense-specific memory metrics.

    Attributes:
        system_cpu_active_percentage (str): Overall CPU active percentage.
        system_disk_total_bytes (str): Total disk space in bytes.
        system_disk_used_bytes (str): Used disk space in bytes.
        system_memory_total_bytes (str): Total system memory in bytes.
        system_memory_used_bytes (str): Used system memory in bytes.
        system_network_received_bytes (str): Total network bytes received.
        system_network_sent_bytes (str): Total network bytes sent.
        typesense_memory_active_bytes (str): Active memory used by Typesense.
        typesense_memory_allocated_bytes (str): Allocated memory for Typesense.
        typesense_memory_fragmentation_ratio (str): Memory fragmentation ratio.
        typesense_memory_mapped_bytes (str): Mapped memory in bytes.
        typesense_memory_metadata_bytes (str): Memory used for metadata.
        typesense_memory_resident_bytes (str): Resident memory in bytes.
        typesense_memory_retained_bytes (str): Retained memory in bytes.
    """

    system_cpu_active_percentage: str
    system_disk_total_bytes: str
    system_disk_used_bytes: str
    system_memory_total_bytes: str
    system_memory_used_bytes: str
    system_network_received_bytes: str
    system_network_sent_bytes: str
    typesense_memory_active_bytes: str
    typesense_memory_allocated_bytes: str
    typesense_memory_fragmentation_ratio: str
    typesense_memory_mapped_bytes: str
    typesense_memory_metadata_bytes: str
    typesense_memory_resident_bytes: str
    typesense_memory_retained_bytes: str


class MetricsResponse(MetricsResponseBase):
    """Extended MetricsResponse with optional per-CPU core metrics."""

    system_memory_total_swap_bytes: str
    system_memory_used_swap_bytes: str
    system_cpu1_active_percentage: typing.Optional[str]
    system_cpu2_active_percentage: typing.Optional[str]
    system_cpu3_active_percentage: typing.Optional[str]
    system_cpu4_active_percentage: typing.Optional[str]
    system_cpu5_active_percentage: typing.Optional[str]
    system_cpu6_active_percentage: typing.Optional[str]
    system_cpu7_active_percentage: typing.Optional[str]
    system_cpu8_active_percentage: typing.Optional[str]
    system_cpu9_active_percentage: typing.Optional[str]
    system_cpu10_active_percentage: typing.Optional[str]
    system_cpu11_active_percentage: typing.Optional[str]
    system_cpu12_active_percentage: typing.Optional[str]
    system_cpu13_active_percentage: typing.Optional[str]
    system_cpu14_active_percentage: typing.Optional[str]
    system_cpu15_active_percentage: typing.Optional[str]
    system_cpu16_active_percentage: typing.Optional[str]
    system_cpu17_active_percentage: typing.Optional[str]
    system_cpu18_active_percentage: typing.Optional[str]
    system_cpu19_active_percentage: typing.Optional[str]
    system_cpu20_active_percentage: typing.Optional[str]
    system_cpu21_active_percentage: typing.Optional[str]
    system_cpu22_active_percentage: typing.Optional[str]
    system_cpu23_active_percentage: typing.Optional[str]
    system_cpu24_active_percentage: typing.Optional[str]


class Metrics:
    """
    Manages metrics retrieval from the Typesense API.

    This class provides methods to retrieve system and Typesense metrics
    such as CPU, memory, disk, and network usage.

    Attributes:
        resource_path (str): The base path for metrics endpoint.
        api_call (ApiCall): The ApiCall instance for making API requests.
    """

    resource_path: typing.Final[str] = "/metrics.json"

    def __init__(self, api_call: ApiCall):
        """
        Initialize the Metrics instance.

        Args:
            api_call (ApiCall): The ApiCall instance for making API requests.
        """
        self.api_call = api_call

    def retrieve(self) -> MetricsResponse:
        """
        Retrieve metrics from the Typesense API.

        Returns:
            MetricsResponse: A dictionary containing system and Typesense metrics.
        """
        response: MetricsResponse = self.api_call.get(
            Metrics.resource_path,
            as_json=True,
            entity_type=MetricsResponse,
        )
        return response
