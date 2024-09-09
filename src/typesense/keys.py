"""
This module provides functionality for managing API keys in Typesense.

Classes:
    - Keys: Handles operations related to API keys.

Methods:
    - __init__: Initializes the Keys object.
    - __getitem__: Retrieves or creates a Key object for a given key_id.
    - create: Creates a new API key.
    - generate_scoped_search_key: Generates a scoped search key.
    - retrieve: Retrieves all API keys.

Attributes:
    - resource_path: The API resource path for key operations.

The Keys class interacts with the Typesense API to manage API key operations.
It provides methods to create, retrieve, and generate scoped search keys, as well as
access individual Key objects.

This module uses type hinting and is compatible with Python 3.11+ as well as earlier
versions through the use of the typing_extensions library.
"""

import base64
import hashlib
import hmac
import json
import sys

from typesense.api_call import ApiCall
from typesense.key import Key
from typesense.types.document import GenerateScopedSearchKeyParams
from typesense.types.key import (
    ApiKeyCreateResponseSchema,
    ApiKeyCreateSchema,
    ApiKeyRetrieveSchema,
    ApiKeySchema,
)

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing


class Keys:
    """
    Class for managing API keys in Typesense.

    This class provides methods to interact with API keys, including
    creating, retrieving, and generating scoped search keys.

    Attributes:
        resource_path (str): The API resource path for key operations.
        api_call (ApiCall): The API call object for making requests.
        keys (Dict[int, Key]): A dictionary of Key objects.
    """

    resource_path: typing.Final[str] = "/keys"

    def __init__(self, api_call: ApiCall) -> None:
        """
        Initialize the Keys object.

        Args:
            api_call (ApiCall): The API call object for making requests.
        """
        self.api_call = api_call
        self.keys: typing.Dict[int, Key] = {}

    def __getitem__(self, key_id: int) -> Key:
        """
        Get or create a Key object for a given key_id.

        Args:
            key_id (int): The ID of the API key.

        Returns:
            Key: The Key object for the given ID.
        """
        if not self.keys.get(key_id):
            self.keys[key_id] = Key(self.api_call, key_id)
        return self.keys[key_id]

    def create(self, schema: ApiKeyCreateSchema) -> ApiKeyCreateResponseSchema:
        """
        Create a new API key.

        Args:
            schema (ApiKeyCreateSchema): The schema for creating the API key.

        Returns:
            ApiKeyCreateResponseSchema: The created API key.
        """
        response: ApiKeySchema = self.api_call.post(
            Keys.resource_path,
            as_json=True,
            body=schema,
            entity_type=ApiKeySchema,
        )
        return response

    def generate_scoped_search_key(
        self,
        search_key: str,
        key_parameters: GenerateScopedSearchKeyParams,
    ) -> bytes:
        """
        Generate a scoped search key.

        Note: only a key generated with the `documents:search`
          action will be accepted by the server.

        Args:
            search_key (str): The search key to use as a base.
            key_parameters (GenerateScopedSearchKeyParams): Parameters for the scoped key.

        Returns:
            bytes: The generated scoped search key.
        """
        params_str = json.dumps(key_parameters)
        digest = base64.b64encode(
            hmac.new(
                search_key.encode("utf-8"),
                params_str.encode("utf-8"),
                digestmod=hashlib.sha256,
            ).digest(),
        )
        key_prefix = search_key[:4]
        raw_scoped_key = f"{digest.decode('utf-8')}{key_prefix}{params_str}"
        return base64.b64encode(raw_scoped_key.encode("utf-8"))

    def retrieve(self) -> ApiKeyRetrieveSchema:
        """
        Retrieve all API keys.

        Returns:
            ApiKeyRetrieveSchema: The schema containing all API keys.
        """
        response: ApiKeyRetrieveSchema = self.api_call.get(
            Keys.resource_path,
            entity_type=ApiKeyRetrieveSchema,
            as_json=True,
        )
        return response
