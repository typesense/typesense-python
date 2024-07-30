"""Tests for the Node class."""

import time

import pytest

from tests.utils.object_assertions import assert_match_object, assert_to_contain_object
from typesense.configuration import Node
from typesense.exceptions import ConfigError


def test_node_initialization() -> None:
    """Test the initialization of the Node class using an object."""
    node = Node(host="localhost", port=8108, path="/path", protocol="http")

    current_time = int(time.time())
    expected = {
        "host": "localhost",
        "port": 8108,
        "path": "/path",
        "protocol": "http",
        "healthy": True,
        "last_access_ts": current_time,
    }
    assert_match_object(node, expected)


def test_node_from_url() -> None:
    """Test the initialization of the Node class using a URL."""
    node = Node.from_url("http://localhost:8108/path")

    current_time = int(time.time())
    expected = {
        "host": "localhost",
        "port": 8108,
        "path": "/path",
        "protocol": "http",
        "healthy": True,
        "last_access_ts": current_time,
    }
    assert_match_object(node, expected)


def test_node_from_url_missing_hostname() -> None:
    """Test the initialization of the Node class using a URL without a host name."""
    with pytest.raises(ConfigError, match="Node URL does not contain the host name."):
        Node.from_url("http://:8108/path")


def test_node_from_url_missing_port() -> None:
    """Test the initialization of the Node class using a URL without a port."""
    with pytest.raises(ConfigError, match="Node URL does not contain the port."):
        Node.from_url("http://localhost:/path")


def test_node_from_url_missing_scheme() -> None:
    """Test the initialization of the Node class using a URL without a scheme."""
    with pytest.raises(ConfigError, match="Node URL does not contain the protocol."):
        Node.from_url("//localhost:8108/path")


def test_node_url() -> None:
    """Test the URL method of the Node class."""
    node = Node(host="localhost", port=8108, path="/path", protocol="http")
    assert node.url() == "http://localhost:8108/path"
