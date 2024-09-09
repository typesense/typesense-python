"""
This module provides functionality for managing individual API keys in Typesense.

Classes:
    - Key: Handles operations related to a specific API key.

Methods:
    - __init__: Initializes the Key object.
    - _endpoint_path: Constructs the API endpoint path for this specific key.
    - retrieve: Retrieves the details of this specific API key.
    - delete: Deletes this specific API key.

The Key class interacts with the Typesense API to manage operations on a
specific API key. It provides methods to retrieve and delete individual keys.

This module uses type hinting and is compatible with Python 3.11+ as well as earlier
versions through the use of the typing_extensions library.
"""

from typesense.api_call import ApiCall
from typesense.types.key import ApiKeyDeleteSchema, ApiKeySchema


class Key:
    """
    Class for managing individual API keys in Typesense.

    This class provides methods to interact with a specific API key,
    including retrieving and deleting it.

    Attributes:
        key_id (int): The ID of the API key.
        api_call (ApiCall): The API call object for making requests.
    """

    def __init__(self, api_call: ApiCall, key_id: int) -> None:
        """
        Initialize the Key object.

        Args:
            api_call (ApiCall): The API call object for making requests.
            key_id (int): The ID of the API key.
        """
        self.key_id = key_id
        self.api_call = api_call

    def retrieve(self) -> ApiKeySchema:
        """
        Retrieve this specific API key.

        Returns:
            ApiKeySchema: The schema containing the API key details.
        """
        response: ApiKeySchema = self.api_call.get(
            self._endpoint_path,
            as_json=True,
            entity_type=ApiKeySchema,
        )
        return response

    def delete(self) -> ApiKeyDeleteSchema:
        """
        Delete this specific API key.

        Returns:
            ApiKeyDeleteSchema: The schema containing the deletion response.
        """
        response: ApiKeyDeleteSchema = self.api_call.delete(
            self._endpoint_path,
            entity_type=ApiKeyDeleteSchema,
        )
        return response

    @property
    def _endpoint_path(self) -> str:
        """
        Construct the API endpoint path for this specific API key.

        Returns:
            str: The constructed endpoint path.
        """
        from typesense.keys import Keys

        return "/".join([Keys.resource_path, str(self.key_id)])
