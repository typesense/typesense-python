"""Tests for the Configuration class."""

import types

import pytest

from tests.utils.object_assertions import (
    assert_match_object,
    assert_object_lists_match,
    assert_to_contain_object,
)
from typesense.configuration import ConfigDict, Configuration, Node
from typesense.exceptions import ConfigError

DEFAULT_NODE = types.MappingProxyType(
    {"host": "localhost", "port": 8108, "protocol": "http"},
)


def test_configuration_defaults() -> None:
    """Test the Configuration constructor defaults."""
    config: ConfigDict = {
        "nodes": [
            {
                "host": "localhost",
                "port": 8108,
                "protocol": "http",
                "path": "3",
            },
            DEFAULT_NODE,
        ],
        "nearest_node": DEFAULT_NODE,
        "api_key": "xyz",
    }

    configuration = Configuration(config)

    nodes = [
        Node(host="localhost", port=8108, protocol="http", path=""),
        Node(host="localhost", port=8108, protocol="http", path="3"),
    ]
    nearest_node = Node(host="localhost", port=8108, protocol="http", path="")

    assert_object_lists_match(configuration.nodes, nodes)

    assert_match_object(configuration.nearest_node, nearest_node)

    expected = {
        "api_key": "xyz",
        "connection_timeout_seconds": 3.0,
        "num_retries": 3,
        "retry_interval_seconds": 1.0,
        "verify": True,
    }

    assert_to_contain_object(configuration, expected)


def test_configuration_explicit() -> None:
    """Test the Configuration constructor with explicit values."""
    config: ConfigDict = {
        "nodes": [DEFAULT_NODE],
        "nearest_node": DEFAULT_NODE,
        "api_key": "xyz",
        "connection_timeout_seconds": 5.0,
        "num_retries": 5,
        "retry_interval_seconds": 2.0,
        "verify": False,
        "additional_headers": {"X-Test": "test", "X-Test2": "test2"},
    }

    configuration = Configuration(config)

    nodes = [Node(host="localhost", port=8108, protocol="http", path="")]
    nearest_node = Node(host="localhost", port=8108, protocol="http", path="")

    assert_object_lists_match(configuration.nodes, nodes)
    assert_match_object(configuration.nearest_node, nearest_node)

    expected = {
        "api_key": "xyz",
        "connection_timeout_seconds": 5.0,
        "num_retries": 5,
        "retry_interval_seconds": 2.0,
        "verify": False,
        "additional_headers": {"X-Test": "test", "X-Test2": "test2"},
    }

    assert_to_contain_object(configuration, expected)


def test_configuration_no_nearest_node() -> None:
    """Test the Configuration constructor with no nearest node."""
    config: ConfigDict = {
        "nodes": [DEFAULT_NODE],
        "api_key": "xyz",
    }

    configuration = Configuration(config)

    nodes = Node(host="localhost", port=8108, protocol="http", path="")

    for node in configuration.nodes:
        assert_match_object(node, nodes)

    expected = {
        "api_key": "xyz",
        "connection_timeout_seconds": 3.0,
        "num_retries": 3,
        "retry_interval_seconds": 1.0,
        "verify": True,
        "nearest_node": None,
    }
    assert_to_contain_object(configuration, expected)


def test_configuration_empty_nodes() -> None:
    """Test the Configuration constructor with empty nodes."""
    config: ConfigDict = {
        "nodes": [],
        "api_key": "xyz",
    }

    with pytest.raises(
        ConfigError,
        match="`nodes` is not defined.",  # noqa: B950
    ):
        Configuration(config)


def test_configuration_invalid_node() -> None:
    """Test the Configuration constructor with an invalid node."""
    config: ConfigDict = {
        "nodes": [{"host": "localhost"}],
        "api_key": "xyz",
    }

    with pytest.raises(
        ConfigError,
        match="`node` entry must be a URL string or a dictionary with the following required keys: host, port, protocol",  # noqa: B950
    ):
        Configuration(config)


def test_configuration_invalid_node_url() -> None:
    """Test the Configuration constructor with an invalid node as a url."""
    config: ConfigDict = {
        "nodes": ["http://localhost"],
        "api_key": "xyz",
    }

    with pytest.raises(
        ConfigError,
        match="Node URL does not contain the port.",
    ):
        Configuration(config)


def test_configuration_invalid_nearest_node() -> None:
    """Test the Configuration constructor with an invalid nearest node."""
    config: ConfigDict = {
        "nodes": [DEFAULT_NODE],
        "nearest_node": {"host": "localhost"},
        "api_key": "xyz",
    }

    with pytest.raises(
        ConfigError,
        match="`nearest_node` entry must be a URL string or a dictionary with the following required keys: host, port, protocol",  # noqa: B950
    ):
        Configuration(config)


def test_configuration_invalid_nearest_node_url() -> None:
    """Test the Configuration constructor with an invalid nearest node as a url."""
    config: ConfigDict = {
        "nodes": [DEFAULT_NODE],
        "nearest_node": "http://localhost",
        "api_key": "xyz",
    }

    with pytest.raises(
        ConfigError,
        match="Node URL does not contain the port.",
    ):
        Configuration(config)
