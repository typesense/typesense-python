import pytest

from src.typesense.configuration import Node
from src.typesense.exceptions import ConfigError


def test_node_initialization() -> None:
    node = Node(host="localhost", port=8108, path="/path", protocol="http")
    assert node.host == "localhost"
    assert node.port == 8108
    assert node.path == "/path"
    assert node.protocol == "http"
    assert node.healthy is True


def test_node_from_url() -> None:
    node = Node.from_url("http://localhost:8108/path")
    assert node.host == "localhost"
    assert node.port == 8108
    assert node.path == "/path"
    assert node.protocol == "http"


def test_node_from_url_missing_hostname() -> None:
    with pytest.raises(ConfigError, match="Node URL does not contain the host name."):
        Node.from_url("http://:8108/path")


def test_node_from_url_missing_port() -> None:
    with pytest.raises(ConfigError, match="Node URL does not contain the port."):
        Node.from_url("http://localhost:/path")


def test_node_from_url_missing_scheme() -> None:
    with pytest.raises(ConfigError, match="Node URL does not contain the protocol."):
        Node.from_url("//localhost:8108/path")


def test_node_url() -> None:
    node = Node(host="localhost", port=8108, path="/path", protocol="http")
    assert node.url() == "http://localhost:8108/path"
