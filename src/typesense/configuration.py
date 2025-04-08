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

import sys
import time

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

from urllib.parse import urlparse

from typesense.exceptions import ConfigError
from typesense.logger import logger


class NodeConfigDict(typing.TypedDict):
    """
    A dictionary that represents the configuration for a node in the Typesense cluster.

    Attributes:
        host (str): The host name of the node.
        port (int): The port number of the node.
        path (str, optional): The path of the node.
        protocol (typing.Literal['http', 'https'] | str): The protocol of the node.
    """

    host: str
    port: int
    path: typing.NotRequired[str]
    protocol: typing.Union[typing.Literal["http", "https"], str]


class ConfigDict(typing.TypedDict):
    """
    A dictionary that represents the configuration for the Typesense client.

    Attributes:
        nodes (list[typing.Union[str, NodeConfigDict]]): A list of dictionaries or URLs that
            represent the nodes in the cluster.

        nearest_node (typing.Union[str, NodeConfigDict]): A dictionary or URL
            that represents the nearest node to the client.

        api_key (str): The API key to use for authentication.

        num_retries (int): The number of retries to attempt before failing.

        interval_seconds (int): The interval in seconds between retries.

        healthcheck_interval_seconds (int): The interval in seconds between
            health checks.

        verify (bool): Whether to verify the SSL certificate.

        timeout_seconds (int, deprecated): The connection timeout in seconds.

        master_node (typing.Union[str, NodeConfigDict], deprecated): A dictionary or
            URL that represents the master node.

        additional_headers (dict): Additional headers to include in the request.

        read_replica_nodes (list[typing.Union[str, NodeConfigDict]], deprecated): A list of
            dictionaries or URLs that represent the read replica nodes.

        connection_timeout_seconds (float): The connection timeout in seconds.
    """

    nodes: typing.List[typing.Union[str, NodeConfigDict]]
    nearest_node: typing.NotRequired[typing.Union[str, NodeConfigDict]]
    api_key: str
    num_retries: typing.NotRequired[int]
    interval_seconds: typing.NotRequired[int]
    healthcheck_interval_seconds: typing.NotRequired[int]
    verify: typing.NotRequired[bool]
    timeout_seconds: typing.NotRequired[int]  # deprecated
    master_node: typing.NotRequired[typing.Union[str, NodeConfigDict]]  # deprecated
    additional_headers: typing.NotRequired[typing.Dict[str, str]]
    read_replica_nodes: typing.NotRequired[
        typing.List[typing.Union[str, NodeConfigDict]]
    ]  # deprecated
    connection_timeout_seconds: typing.NotRequired[float]


class Node:
    """
    Class for representing a node in the Typesense cluster.

    Attributes:
        host (str): The host name of the node.
        port (str | int): The port number of the node.
        path (str): The path of the node.
        protocol (typing.Literal['http', 'https'] | str): The protocol of the node.
        healthy (bool): Whether the node is healthy or not.
    """

    def __init__(
        self,
        host: str,
        port: typing.Union[str, int],
        path: str,
        protocol: typing.Union[typing.Literal["http", "https"], str],
    ) -> None:
        """
        Initialize a Node object with the specified host, port, path, and protocol.

        Args:
            host (str): The host name of the node.
            port (str | int): The port number of the node.
            path (str): The path of the node.
            protocol (typing.Literal['http', 'https'] | str): The protocol of the node.
        """
        self.host = host
        self.port = port
        self.path = path
        self.protocol = protocol

        # Used to skip bad hosts
        self.healthy = True

        # Used to track the last time this node was accessed
        self.last_access_ts: int = int(time.time())

    @classmethod
    def from_url(cls, url: str) -> "Node":
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
            raise ConfigError("Node URL does not contain the host name.")
        if not parsed.port:
            raise ConfigError("Node URL does not contain the port.")
        if not parsed.scheme:
            raise ConfigError("Node URL does not contain the protocol.")

        return cls(parsed.hostname, parsed.port, parsed.path, parsed.scheme)

    def url(self) -> str:
        """
        Generate the URL of the node.

        Returns:
            str: The URL of the node
        """
        return f"{self.protocol}://{self.host}:{self.port}{self.path}"


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

    def __init__(
        self,
        config_dict: ConfigDict,
    ) -> None:
        """
        Initialize a Configuration object with the specified configuration settings.

        Args:
            config_dict (ConfigDict): A dictionary containing the configuration settings.
        """
        self.validations = ConfigurationValidations
        self.validations.show_deprecation_warnings(config_dict)
        self.validations.validate_config_dict(config_dict)

        self.nodes: typing.List[Node] = [
            self._initialize_nodes(node) for node in config_dict["nodes"]
        ]

        nearest_node = config_dict.get("nearest_node", None)

        self.nearest_node = self._handle_nearest_node(nearest_node)
        self.api_key = config_dict.get("api_key", " ")
        self.connection_timeout_seconds = config_dict.get(
            "connection_timeout_seconds",
            3.0,
        )
        self.num_retries = config_dict.get("num_retries", 3)
        self.retry_interval_seconds = config_dict.get("retry_interval_seconds", 1.0)
        self.healthcheck_interval_seconds = config_dict.get(
            "healthcheck_interval_seconds",
            60,
        )
        self.verify = config_dict.get("verify", True)
        self.additional_headers = config_dict.get("additional_headers", {})

    def _handle_nearest_node(
        self,
        nearest_node: typing.Union[str, NodeConfigDict, None],
    ) -> typing.Union[Node, None]:
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
        node: typing.Union[str, NodeConfigDict],
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
            node["host"],
            node["port"],
            node.get("path", ""),
            node["protocol"],
        )


class ConfigurationValidations:
    """Class for validating the configuration dictionary."""

    @staticmethod
    def validate_config_dict(config_dict: ConfigDict) -> None:
        """
        Validate the configuration dictionary to ensure it contains the required fields.

        Args:
            config_dict (ConfigDict): The configuration dictionary to validate.

        Raises:
            ConfigError: If the configuration dictionary is missing required fields.
        """
        ConfigurationValidations.validate_required_config_fields(config_dict)
        ConfigurationValidations.validate_nodes(config_dict["nodes"])

        nearest_node = config_dict.get("nearest_node", None)
        if nearest_node:
            ConfigurationValidations.validate_nearest_node(nearest_node)

    @staticmethod
    def validate_required_config_fields(config_dict: ConfigDict) -> None:
        """
        Validate the presence of required fields in the configuration dictionary.

        Args:
            config_dict (ConfigDict): The configuration dictionary to validate.

        Raises:
            ConfigError: If the configuration dictionary is missing required fields.
        """
        if not config_dict.get("nodes"):
            raise ConfigError("`nodes` is not defined.")

        if not config_dict.get("api_key"):
            raise ConfigError("`api_key` is not defined.")

    @staticmethod
    def validate_nodes(nodes: typing.List[typing.Union[str, NodeConfigDict]]) -> None:
        """
        Validate the nodes in the configuration dictionary.

        Args:
            nodes (list): The list of nodes to validate.

        Raises:
            ConfigError: If any node is invalid.
        """
        for node in nodes:
            if not ConfigurationValidations.validate_node_fields(node):
                raise ConfigError(
                    " ".join(
                        [
                            "`node` entry must be a URL string or a",
                            "dictionary with the following required keys:",
                            "host, port, protocol",
                        ],
                    ),
                )

    @staticmethod
    def validate_nearest_node(nearest_node: typing.Union[str, NodeConfigDict]) -> None:
        """
        Validate the nearest node in the configuration dictionary.

        Args:
            nearest_node (dict): The nearest node to validate.

        Raises:
            ConfigError: If the nearest node is invalid.
        """
        if not ConfigurationValidations.validate_node_fields(nearest_node):
            raise ConfigError(
                " ".join(
                    [
                        "`nearest_node` entry must be a URL string or a dictionary",
                        "with the following required keys:",
                        "host, port, protocol",
                    ],
                ),
            )

    @staticmethod
    def validate_node_fields(node: typing.Union[str, NodeConfigDict]) -> bool:
        """
        Validate the fields of a node in the configuration dictionary.

        Args:
            node (str | NodeConfigDict): The node to validate.

        Returns:
            bool: True if the node is valid, False otherwise.
        """
        if isinstance(node, str):
            return True
        expected_fields = {"host", "port", "protocol"}
        return expected_fields.issubset(node)

    @staticmethod
    def show_deprecation_warnings(config_dict: ConfigDict) -> None:
        """
        Show deprecation warnings for deprecated configuration fields.

        Args:
            config_dict (ConfigDict): The configuration dictionary
                to check for deprecated fields.
        """
        if config_dict.get("timeout_seconds"):
            logger.warn(
                " ".join(
                    [
                        "Deprecation warning: timeout_seconds is now renamed",
                        "to connection_timeout_seconds",
                    ],
                ),
            )

        if config_dict.get("master_node"):
            logger.warn(
                " ".join(
                    [
                        "Deprecation warning: master_node is now consolidated",
                        "to nodes,starting with Typesense Server v0.12",
                    ],
                ),
            )

        if config_dict.get("read_replica_nodes"):
            logger.warn(
                " ".join(
                    [
                        "Deprecation warning: read_replica_nodes is now",
                        "consolidated to nodes, starting with Typesense Server v0.12",
                    ],
                ),
            )
