"""
This module provides functionality for accessing debug information in Typesense.

Classes:
    - Debug: Handles operations related to retrieving debug information.

Methods:
    - __init__: Initializes the Debug object.
    - retrieve: Retrieves debug information from the Typesense server.

Attributes:
    - RESOURCE_PATH: The API resource path for debug operations.

The Debug class interacts with the Typesense API to fetch debug information,
which can be useful for troubleshooting and system monitoring.

This module uses type hinting and is compatible with Python 3.11+ as well as earlier
versions through the use of the typing_extensions library.
"""

from typing import Final

from typesense.api_call import ApiCall
from typesense.types.debug import DebugResponseSchema


class Debug:
    """
    Class for accessing debug information in Typesense.

    This class provides methods to retrieve debug information from the Typesense server,
    which can be useful for system diagnostics and troubleshooting.

    Attributes:
        RESOURCE_PATH (str): The API resource path for debug operations.
        api_call (ApiCall): The API call object for making requests.
    """

    resource_path: Final[str] = "/debug"

    def __init__(self, api_call: ApiCall) -> None:
        """
        Initialize the Debug object.

        Args:
            api_call (ApiCall): The API call object for making requests.
        """
        self.api_call = api_call

    def retrieve(self) -> DebugResponseSchema:
        """
        Retrieve debug information from the Typesense server.

        This method sends a GET request to the debug endpoint and returns
        the server's debug information.

        Returns:
            DebugResponseSchema: A schema containing the debug information.
        """
        return self.api_call.get(
            Debug.resource_path,
            as_json=True,
            entity_type=DebugResponseSchema,
        )
