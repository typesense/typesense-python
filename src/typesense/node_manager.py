"""
This module provides functionality for managing nodes in a Typesense cluster configuration.

It contains the NodeManager class, which is responsible for node selection, health checks,
and rotation strategies for load balancing and fault tolerance in a Typesense cluster.

Key features:
- Round-robin node selection
- Nearest node prioritization (if configured)
- Node health tracking and updates
- Periodic health checks based on a configurable interval

Classes:
    NodeManager: Manages the nodes in a Typesense cluster configuration.

Dependencies:
    - typesense.configuration: Provides Configuration and Node classes
    - typesense.logger: Provides logging functionality

Usage:
    from typesense.configuration import Configuration
    from node_manager import NodeManager

    config = Configuration(...)
    node_manager = NodeManager(config)
    node = node_manager.get_node()

Note: This module is part of the Typesense Python client library and is
used internally by other components of the library.
"""

import copy
import time

from typesense.configuration import Configuration, Node
from typesense.logger import logger


class NodeManager:
    """
    Manages the nodes in a Typesense cluster configuration.

    This class handles node selection, health checks, and rotation for load balancing
    and fault tolerance in a Typesense cluster.

    Attributes:
        config (Configuration): The configuration object for the Typesense client.
        nodes (List[Node]): A copy of the nodes from the configuration.
        node_index (int): The index of the current node in the rotation.
    """

    def __init__(self, config: Configuration):
        """
        Initialize the NodeManager with a given configuration.

        Args:
            config (Configuration): The configuration object for the Typesense client.
        """
        self.config = config
        self.nodes = copy.deepcopy(config.nodes)
        self.node_index = 0
        self._initialize_nodes()

    def get_node(self) -> Node:
        """
        Get the next available healthy node.

        This method implements a round-robin selection strategy, prioritizing the nearest node
        if configured, and considering the health status of each node.

        Returns:
            Node: The selected node for the next operation.
        """
        if self.config.nearest_node:
            if self.config.nearest_node.healthy or self._is_due_for_health_check(
                self.config.nearest_node,
            ):
                return self.config.nearest_node

        node_index = 0
        while node_index < len(self.nodes):
            node_index += 1
            node = self.nodes[self.node_index]
            self.node_index = (self.node_index + 1) % len(self.nodes)
            if node.healthy or self._is_due_for_health_check(node):
                return node

        logger.debug("No healthy nodes were found. Returning the next node.")
        return self.nodes[self.node_index]

    def set_node_health(self, node: Node, is_healthy: bool) -> None:
        """
        Set the health status of a node and update its last access timestamp.

        Args:
            node (Node): The node to update.
            is_healthy (bool): The health status to set for the node.
        """
        node.healthy = is_healthy
        node.last_access_ts = int(time.time())

    def _is_due_for_health_check(self, node: Node) -> bool:
        """
        Check if a node is due for a health check based on the configured interval.

        Args:
            node (Node): The node to check.

        Returns:
            bool: True if the node is due for a health check, False otherwise.
        """
        current_epoch_ts = int(time.time())
        return bool(
            (current_epoch_ts - node.last_access_ts)
            > self.config.healthcheck_interval_seconds,
        )

    def _initialize_nodes(self) -> None:
        """
        Initialize all nodes as healthy.

        This method sets the initial health status of all nodes, including the nearest node
        if configured, to healthy.
        """
        if self.config.nearest_node:
            self.set_node_health(self.config.nearest_node, is_healthy=True)
        for node in self.nodes:
            self.set_node_health(node, is_healthy=True)
