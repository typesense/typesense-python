"""
This module provides async functionality for managing API keys in Typesense.

It contains the Keys class, which allows for creating, retrieving, and
generating scoped search keys asynchronously.

Classes:
    Keys: Manages API keys in the Typesense API (async).

Dependencies:
    - typesense.async_api_call: Provides the ApiCall class for making async API requests.
    - typesense.async_key: Provides the Key class for individual API key operations.
    - typesense.types.document: Provides GenerateScopedSearchKeyParams type.
    - typesense.types.key: Provides various API key schema types.

Note: This module uses conditional imports to support both Python 3.11+ and earlier versions.
"""

import base64
import hashlib
import hmac
import json
import sys

from .api_call import ApiCall
from .key import Key
from typesense.types.document import GenerateScopedSearchKeyParams
from typesense.types.key import (
    ApiKeyCreateResponseSchema,
    ApiKeyCreateSchema,
    ApiKeyRetrieveSchema,
)

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing


class Keys:
    """
    Manages API keys in the Typesense API (async).

    This class provides async methods to create, retrieve, and generate scoped search keys.

    Attributes:
        resource_path (str): The API endpoint path for key operations.
        api_call (ApiCall): The ApiCall instance for making async API requests.
        keys (Dict[int, Key]): A dictionary of Key instances, keyed by key ID.
    """

    resource_path: typing.Final[str] = "/keys"

    def __init__(self, api_call: ApiCall) -> None:
        """
        Initialize the Keys instance.

        Args:
            api_call (ApiCall): The ApiCall instance for making async API requests.
        """
        self.api_call = api_call
        self.keys: typing.Dict[int, Key] = {}

    def __getitem__(self, key_id: int) -> Key:
        """
        Get or create an Key instance for a given key ID.

        This method allows accessing API keys using dictionary-like syntax.
        If the Key instance doesn't exist, it creates a new one.

        Args:
            key_id (int): The ID of the API key.

        Returns:
            Key: The Key instance for the specified key ID.

        Example:
            >>> keys = Keys(async_api_call)
            >>> key = keys[1]
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

        Example:
            >>> keys = Keys(async_api_call)
            >>> key = await keys.create(
            ...     {
            ...         "actions": ["documents:search"],
            ...         "collections": ["companies"],
            ...         "description": "Search-only key",
            ...     }
            ... )
        """
        response: ApiKeyCreateResponseSchema = self.api_call.post(
            Keys.resource_path,
            as_json=True,
            body=schema,
            entity_type=ApiKeyCreateResponseSchema,
        )
        return response

    def generate_scoped_search_key(
        self,
        search_key: str,
        key_parameters: GenerateScopedSearchKeyParams,
    ) -> bytes:
        """
        Generate a scoped search key.

        Note: This is a synchronous method as it performs local computation
        and does not make any API calls. Only a key generated with the
        `documents:search` action will be accepted by the server.

        Args:
            search_key (str): The search key to use as a base.
            key_parameters (GenerateScopedSearchKeyParams): Parameters for the scoped key.

        Returns:
            bytes: The generated scoped search key.

        Example:
            >>> keys = Keys(async_api_call)
            >>> scoped_key = keys.generate_scoped_search_key(
            ...     "KmacipDKNqAM3YiigXfw5pZvNOrPQUba",
            ...     {"q": "search query", "collection": "companies"},
            ... )
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

        Example:
            >>> keys = Keys(async_api_call)
            >>> all_keys = await keys.retrieve()
            >>> for key in all_keys["keys"]:
            ...     print(key["id"])
        """
        response: ApiKeyRetrieveSchema = self.api_call.get(
            Keys.resource_path,
            entity_type=ApiKeyRetrieveSchema,
            as_json=True,
        )
        return response
