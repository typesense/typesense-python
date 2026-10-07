"""
This module provides async functionality for managing overrides in Typesense.

Classes:
    - AsyncOverrides: Handles async operations related to overrides within a collection.

Methods:
    - __init__: Initializes the AsyncOverrides object.
    - __getitem__: Retrieves or creates an AsyncOverride object for a given override_id.
    - _endpoint_path: Constructs the API endpoint path for override operations.
    - upsert: Creates or updates an override.
    - retrieve: Retrieves all overrides for the collection.

Attributes:
    - RESOURCE_PATH: The API resource path for overrides.

The AsyncOverrides class interacts with the Typesense API to manage override operations
within a specific collection. It provides methods to create, update, and retrieve
overrides, as well as access individual AsyncOverride objects.

For more information regarding Overrides, refer to the Curation [documentation]
(https://typesense.org/docs/27.0/api/curation.html#curation).

This module uses type hinting and is compatible with Python 3.11+ as well as earlier
versions through the use of the typing_extensions library.
"""

import sys

from typing_extensions import deprecated

from .api_call import AsyncApiCall
from .override import AsyncOverride
from typesense.logger import warn_deprecation
from typesense.types.override import (
    OverrideCreateSchema,
    OverrideRetrieveSchema,
    OverrideSchema,
)

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing


@deprecated("AsyncOverrides is deprecated on v30+. Use client.curation_sets instead.")
class AsyncOverrides:
    """
    Class for managing overrides in a Typesense collection (async).

    This class provides methods to interact with overrides, including
    retrieving, creating, and updating them.

    Attributes:
        RESOURCE_PATH (str): The API resource path for overrides.
        api_call (AsyncApiCall): The API call object for making requests.
        collection_name (str): The name of the collection.
        overrides (Dict[str, AsyncOverride]): A dictionary of AsyncOverride objects.
    """

    resource_path: typing.Final[str] = "overrides"

    def __init__(
        self,
        api_call: AsyncApiCall,
        collection_name: str,
    ) -> None:
        """
        Initialize the AsyncOverrides object.

        Args:
            api_call (AsyncApiCall): The API call object for making requests.
            collection_name (str): The name of the collection.
        """
        self.api_call = api_call
        self.collection_name = collection_name
        self.overrides: typing.Dict[str, AsyncOverride] = {}

    def __getitem__(self, override_id: str) -> AsyncOverride:
        """
        Get or create an AsyncOverride object for a given override_id.

        Args:
            override_id (str): The ID of the override.

        Returns:
            AsyncOverride: The AsyncOverride object for the given ID.
        """
        if not self.overrides.get(override_id):
            self.overrides[override_id] = AsyncOverride(
                self.api_call,
                self.collection_name,
                override_id,
            )
        return self.overrides[override_id]

    async def upsert(
        self, override_id: str, schema: OverrideCreateSchema
    ) -> OverrideSchema:
        """
        Create or update an override.

        Args:
            id (str): The ID of the override.
            schema (OverrideCreateSchema): The schema for creating or updating the override.

        Returns:
            OverrideSchema: The created or updated override.
        """
        response: OverrideSchema = await self.api_call.put(
            endpoint=self._endpoint_path(override_id),
            entity_type=OverrideSchema,
            body=schema,
        )
        return response

    async def retrieve(self) -> OverrideRetrieveSchema:
        """
        Retrieve all overrides for the collection.

        Returns:
            OverrideRetrieveSchema: The schema containing all overrides.
        """
        response: OverrideRetrieveSchema = await self.api_call.get(
            self._endpoint_path(),
            entity_type=OverrideRetrieveSchema,
            as_json=True,
        )
        return response

    @warn_deprecation(
        "AsyncOverrides is deprecated on v30+. Use client.curation_sets instead.",
        flag_name="overrides_deprecation",
    )
    def _endpoint_path(self, override_id: typing.Union[str, None] = None) -> str:
        """
        Construct the API endpoint path for override operations.

        Args:
            override_id (Union[str, None], optional): The ID of the override. Defaults to None.

        Returns:
            str: The constructed endpoint path.
        """
        from .collections import AsyncCollections

        override_id = override_id or ""

        return "/".join(
            [
                AsyncCollections.resource_path,
                self.collection_name,
                AsyncOverrides.resource_path,
                override_id,
            ],
        )
