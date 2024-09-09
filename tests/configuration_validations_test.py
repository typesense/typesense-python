"""Tests for the ConfigurationValidations class."""

import types

import pytest

from typesense.configuration import ConfigDict, ConfigurationValidations
from typesense.exceptions import ConfigError

DEFAULT_NODE = types.MappingProxyType(
    {"host": "localhost", "port": 8108, "protocol": "http"},
)


def test_validate_node_fields_with_url() -> None:
    """Test validate_node_fields with a URL string."""
    assert ConfigurationValidations.validate_node_fields("http://localhost:8108/path")


def test_validate_node_fields_with_valid_dict() -> None:
    """Test validate_node_fields with a valid dictionary."""
    assert ConfigurationValidations.validate_node_fields(
        DEFAULT_NODE,
    )


def test_validate_node_fields_with_invalid_dict() -> None:
    """Test validate_node_fields with an invalid dictionary."""
    assert not ConfigurationValidations.validate_node_fields(
        {
            "host": "localhost",
            "port": 8108,
        },
    )


def test_deprecation_warning_timeout_seconds(caplog: pytest.LogCaptureFixture) -> None:
    """Test that a deprecation warning is issued for the 'timeout_seconds' field."""
    config_dict: ConfigDict = {
        "nodes": [DEFAULT_NODE],
        "nearest_node": "http://localhost:8108",
        "api_key": "xyz",
        "timeout_seconds": 10,
    }
    ConfigurationValidations.show_deprecation_warnings(config_dict)
    assert (
        ' '.join(
            [
                "Deprecation warning: timeout_seconds is now renamed",
                "to connection_timeout_seconds",
            ],
        )
        in caplog.text
    )


def test_deprecation_warning_master_node(caplog: pytest.LogCaptureFixture) -> None:
    """Test that a deprecation warning is issued for the 'master_node' field."""
    config_dict: ConfigDict = {
        "nodes": [DEFAULT_NODE],
        "nearest_node": "http://localhost:8108",
        "api_key": "xyz",
        "master_node": "http://localhost:8108",
    }
    ConfigurationValidations.show_deprecation_warnings(config_dict)
    assert (
        "Deprecation warning: master_node is now consolidated to nodes" in caplog.text
    )


def test_deprecation_warning_read_replica_nodes(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that a deprecation warning is issued for the 'read_replica_nodes' field."""
    config_dict: ConfigDict = {
        "nodes": [DEFAULT_NODE],
        "nearest_node": "http://localhost:8108",
        "api_key": "xyz",
        "read_replica_nodes": ["http://localhost:8109"],
    }
    ConfigurationValidations.show_deprecation_warnings(config_dict)

    assert (
        "Deprecation warning: read_replica_nodes is now consolidated to nodes"
    ) in caplog.text


def test_validate_config_dict() -> None:
    """Test validate_config_dict."""
    ConfigurationValidations.validate_config_dict(
        {
            "nodes": [
                {
                    "host": "localhost",
                    "port": 8108,
                    "protocol": "http",
                },
            ],
            "nearest_node": {
                "host": "localhost",
                "port": 8108,
                "protocol": "http",
            },
            "api_key": "xyz",
        },
    )


def test_validate_config_dict_with_string_nearest_node() -> None:
    """Test validate_config_dict with nearest node as a string."""
    ConfigurationValidations.validate_config_dict(
        {
            "nodes": [
                {
                    "host": "localhost",
                    "port": 8108,
                    "protocol": "http",
                },
            ],
            "nearest_node": "http://localhost:8108",
            "api_key": "xyz",
        },
    )


def test_validate_config_dict_with_string_nodes() -> None:
    """Test validate_config_dict with nodes as a string."""
    ConfigurationValidations.validate_config_dict(
        {
            "nodes": "http://localhost:8108",
            "nearest_node": "http://localhost:8108",
            "api_key": "xyz",
        },
    )


def test_validate_config_dict_with_no_nodes() -> None:
    """Test validate_config_dict with no nodes."""
    with pytest.raises(ConfigError, match="`nodes` is not defined."):
        ConfigurationValidations.validate_config_dict(
            {
                "nearest_node": "http://localhost:8108",
                "api_key": "xyz",
            },
        )


def test_validate_config_dict_with_no_api_key() -> None:
    """Test validate_config_dict with no api_key."""
    with pytest.raises(ConfigError, match="`api_key` is not defined."):
        ConfigurationValidations.validate_config_dict(
            {
                "nodes": [DEFAULT_NODE],
                "nearest_node": "http://localhost:8108",
            },
        )


def test_validate_config_dict_with_wrong_node() -> None:
    """Test validate_config_dict with wrong node."""
    with pytest.raises(
        ConfigError,
        match="`node` entry must be a URL string or a dictionary with the following required keys: host, port, protocol",  # noqa: B950
    ):
        ConfigurationValidations.validate_config_dict(
            {
                "nodes": [
                    {
                        "host": "localhost",
                        "port": 8108,
                        "wrong_field": "invalid",
                    },
                ],
                "api_key": "xyz",
            },
        )


def test_validate_config_dict_with_wrong_nearest_node() -> None:
    """Test validate_config_dict with wrong nearest node."""
    with pytest.raises(
        ConfigError,
        match='`nearest_node` entry must be a URL string or a dictionary with the following required keys: host, port, protocol',  # noqa: B950
    ):
        ConfigurationValidations.validate_config_dict(
            {
                "nodes": [
                    {
                        "host": "localhost",
                        "port": 8108,
                        "protocol": "http",
                    },
                ],
                "nearest_node": {
                    "host": "localhost",
                    "port": 8108,
                    "wrong_field": "invalid",
                },
                "api_key": "xyz",
            },
        )
