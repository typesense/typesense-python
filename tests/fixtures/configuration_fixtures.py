"""Fixtures for Configuration tests."""

import pytest

from typesense.configuration import ConfigDict, Configuration


@pytest.fixture(scope="function", name="fake_config_dict")
def fake_config_dict_fixture() -> ConfigDict:
    """Return a dictionary with test values."""
    return {
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
    }


@pytest.fixture(scope="function", name="actual_config_dict")
def actual_config_dict_fixture() -> ConfigDict:
    """Return a dictionary with test values."""
    return {
        "api_key": "xyz",
        "nodes": [
            {
                "host": "localhost",
                "port": 8108,
                "protocol": "http",
            },
        ],
    }


@pytest.fixture(scope="function", name="fake_config")
def fake_config_fixture(fake_config_dict: ConfigDict) -> Configuration:
    """Return a Configuration object with test values."""
    return Configuration(
        config_dict=fake_config_dict,
    )


@pytest.fixture(scope="function", name="actual_config")
def actual_config_fixture(actual_config_dict: ConfigDict) -> Configuration:
    """Return a Configuration object using a real API."""
    return Configuration(
        config_dict=actual_config_dict,
    )
