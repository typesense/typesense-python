"""
This module provides configuration management for the Typesense Instance.

Classes:
    - Config: Handles loading and accessing configuration settings.
    - Node: Represents a node in the Typesense cluster.

Functions:
    - load_config: Loads configuration from a file.
    - get_setting: Retrieves a specific setting from the configuration.
    - set_setting: Updates a specific setting in the configuration.

Exceptions:
    - ConfigError: Custom exception for configuration-related errors.
"""

from __future__ import annotations

from typing import Literal, NotRequired, TypedDict, Union
from urllib.parse import urlparse

from typesense.exceptions import ConfigError
from typesense.logger import logger


class NodeConfigDict(TypedDict):
    """
    A dictionary that represents the configuration for a node in the Typesense cluster.

    Attributes:
        host (str): The host name of the node.
        port (int): The port number of the node.
        path (str, optional): The path of the node.
        protocol (Literal['http', 'https'] | str): The protocol of the node.
    """

    host: str
    port: int
    path: NotRequired[str]
    protocol: Literal['http', 'https'] | str


class ConfigDict(TypedDict):
    """
    A dictionary that represents the configuration for the Typesense client.

    Attributes:
        nodes (list[Union[str, NodeConfigDict]]): A list of dictionaries or URLs that
            represent the nodes in the cluster.

        nearest_node (Union[str, NodeConfigDict]): A dictionary or URL
            that represents the nearest node to the client.

        api_key (str): The API key to use for authentication.

        num_retries (int): The number of retries to attempt before failing.

        interval_seconds (int): The interval in seconds between retries.

        healthcheck_interval_seconds (int): The interval in seconds between
            health checks.

        verify (bool): Whether to verify the SSL certificate.

        timeout_seconds (int, deprecated): The connection timeout in seconds.

        master_node (Union[str, NodeConfigDict], deprecated): A dictionary or
            URL that represents the master node.

        read_replica_nodes (list[Union[str, NodeConfigDict]], deprecated): A list of
            dictionaries or URLs that represent the read replica nodes.
    """

    nodes: list[Union[str, NodeConfigDict]]
    nearest_node: NotRequired[Union[str, NodeConfigDict]]
    api_key: str
    num_retries: NotRequired[int]
    interval_seconds: NotRequired[int]
    healthcheck_interval_seconds: NotRequired[int]
    verify: NotRequired[bool]
    timeout_seconds: NotRequired[int]  # deprecated
    master_node: NotRequired[Union[str, NodeConfigDict]]  # deprecated
    read_replica_nodes: NotRequired[list[Union[str, NodeConfigDict]]]  # deprecated


class Node:
    """
    Class for representing a node in the Typesense cluster.

    Attributes:
        host (str): The host name of the node.
        port (str | int): The port number of the node.
        path (str): The path of the node.
        protocol (Literal['http', 'https'] | str): The protocol of the node.
        healthy (bool): Whether the node is healthy or not.
    """

    def __init__(
        self,
        host: str,
        port: str | int,
        path: str,
        protocol: Literal['http', 'https'] | str,
    ) -> None:
        """
        Initialize a Node object with the specified host, port, path, and protocol.

        Args:
            host (str): The host name of the node.
            port (str | int): The port number of the node.
            path (str): The path of the node.
            protocol (Literal['http', 'https'] | str): The protocol of the node.
        """
        self.host = host
        self.port = port
        self.path = path
        self.protocol = protocol

        # Used to skip bad hosts
        self.healthy = True

    @classmethod
    def from_url(cls, url: str) -> 'Node':
        """
        Initialize a Node object from a URL string.

        Args:
            url (str): The URL string to parse.

        Returns:
            Node: The Node object created from the URL string.

        Raises:
            ConfigError: If the URL does not contain the host name, port number, or protocol.
        """
        parsed = urlparse(url)
        if not parsed.hostname:
            raise ConfigError('Node URL does not contain the host name.')
        if not parsed.port:
            raise ConfigError('Node URL does not contain the port.')
        if not parsed.scheme:
            raise ConfigError('Node URL does not contain the protocol.')

        return cls(parsed.hostname, parsed.port, parsed.path, parsed.scheme)

    def url(self) -> str:
        """
        Generate the URL of the node.

        Returns:
            str: The URL of the node
        """
        return f'{self.protocol}://{self.host}:{self.port}{self.path}'


class Configuration:
    """
    Class for managing the configuration settings for the Typesense client.

    Attributes:
        nodes (list[Node]): A list of Node objects representing the nodes in the cluster.
        nearest_node (Node | None): The nearest node to the client.
        api_key (str): The API key to use for authentication.
        connection_timeout_seconds (float): The connection timeout in seconds.
        num_retries (int): The number of retries to attempt before failing.
        retry_interval_seconds (float): The interval in seconds between retries.
        healthcheck_interval_seconds (int): The interval in seconds between health checks.
        verify (bool): Whether to verify the SSL certificate.
    """

    def __init__(self, config_dict: ConfigDict) -> None:
        Configuration.show_deprecation_warnings(config_dict)
        Configuration.validate_config_dict(config_dict)
        """
        Initialize a Configuration object with the specified configuration settings.

        Args:
            config_dict (ConfigDict): A dictionary containing the configuration settings.
        """

        self.nodes: list[Node] = [
            self._initialize_nodes(node) for node in config_dict['nodes']
        ]

        nearest_node = config_dict.get('nearest_node', None)

        self.api_key = config_dict.get('api_key', '')
        self.connection_timeout_seconds = config_dict.get('connection_timeout_seconds', 3.0)
        self.nearest_node = self._handle_nearest_node(nearest_node)
        self.num_retries = config_dict.get('num_retries', 3)
        self.retry_interval_seconds = config_dict.get('retry_interval_seconds', 1.0)
        self.healthcheck_interval_seconds = config_dict.get('healthcheck_interval_seconds', 60)
        self.verify = config_dict.get("verify", True)

    def _handle_nearest_node(
        self,
        nearest_node: Union[str, NodeConfigDict, None],
    ) -> Union[Node, None]:
        """
        Handle the nearest node configuration.

        Args:
            nearest_node (str | NodeConfigDict): The nearest node configuration.

        Returns:
            Node | None: The nearest node object if it exists, None otherwise.
        """
        if nearest_node is None:
            return None
        return self._initialize_nodes(nearest_node)

    def _initialize_nodes(
        self,
        node: Union[str, NodeConfigDict],
    ) -> Node:
        """
        Handle the initialization of a node.

        Args:
            node (Node): The node to initialize.

        Returns:
            Node: The initialized node.
        """
        if isinstance(node, str):
            return Node.from_url(node)

        return Node(
            node['host'],
            node['port'],
            node.get('path', ' '),
            node['protocol'],
        )

    @staticmethod
    def validate_config_dict(config_dict: ConfigDict) -> None:
        nodes = config_dict.get('nodes', None)
        if not nodes:
            raise ConfigError('`nodes` is not defined.')

        api_key = config_dict.get('api_key', None)
        if not api_key:
            raise ConfigError('`api_key` is not defined.')

        for node in nodes:
            if not Configuration.validate_node_fields(node):
                raise ConfigError('`node` entry must be a URL string or a dictionary with the following required keys: '
                                  'host, port, protocol')

        nearest_node = config_dict.get('nearest_node', None)
        if nearest_node and not Configuration.validate_node_fields(nearest_node):
            raise ConfigError('`nearest_node` entry must be a URL string or a dictionary with the following required keys: '
                                  'host, port, protocol')

    @staticmethod
    def validate_node_fields(node: str | NodeConfigDict) -> bool:
        """
        Validate the fields of a node in the configuration dictionary.

        Args:
            node (str | NodeConfigDict): The node to validate.

        Returns:
            bool: True if the node is valid, False otherwise.
        """
        if isinstance(node, str):
            return True
        expected_fields = {'host', 'port', 'protocol'}
        return expected_fields.issubset(node)

    @staticmethod
    def show_deprecation_warnings(config_dict: ConfigDict) -> None:
        """
        Show deprecation warnings for deprecated configuration fields.

        Args:
            config_dict (ConfigDict): The configuration dictionary
                to check for deprecated fields.
        """
        if config_dict.get('timeout_seconds'):
            logger.warn('Deprecation warning: timeout_seconds is now renamed to connection_timeout_seconds')

        if config_dict.get('master_node'):
            logger.warn('Deprecation warning: master_node is now consolidated to nodes, starting with Typesense Server v0.12')

        if config_dict.get('read_replica_nodes'):
            logger.warn('Deprecation warning: read_replica_nodes is now consolidated to nodes, starting with Typesense Server v0.12')
