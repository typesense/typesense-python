"""
This module provides async functionality for managing overrides in Typesense.

Classes:
    - Overrides: Handles async operations related to overrides within a collection.

Methods:
    - __init__: Initializes the Overrides object.
    - __getitem__: Retrieves or creates an Override object for a given override_id.
    - _endpoint_path: Constructs the API endpoint path for override operations.
    - upsert: Creates or updates an override.
    - retrieve: Retrieves all overrides for the collection.

Attributes:
    - RESOURCE_PATH: The API resource path for overrides.

The Overrides class interacts with the Typesense API to manage override operations
within a specific collection. It provides methods to create, update, and retrieve
overrides, as well as access individual Override objects.

For more information regarding Overrides, refer to the Curation [documentation]
(https://typesense.org/docs/27.0/api/curation.html#curation).

This module uses type hinting and is compatible with Python 3.11+ as well as earlier
versions through the use of the typing_extensions library.
"""

import sys

from typing_extensions import deprecated

from .api_call import ApiCall
from .override import Override
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


@deprecated("SyncOverrides is deprecated on v30+. Use client.curation_sets instead.")
class Overrides:
    """
    Class for managing overrides in a Typesense collection (async).

    This class provides methods to interact with overrides, including
    retrieving, creating, and updating them.

    Attributes:
        RESOURCE_PATH (str): The API resource path for overrides.
        api_call (ApiCall): The API call object for making requests.
        collection_name (str): The name of the collection.
        overrides (Dict[str, Override]): A dictionary of Override objects.
    """

    resource_path: typing.Final[str] = "overrides"

    def __init__(
        self,
        api_call: ApiCall,
        collection_name: str,
    ) -> None:
        """
        Initialize the Overrides object.

        Args:
            api_call (ApiCall): The API call object for making requests.
            collection_name (str): The name of the collection.
        """
        self.api_call = api_call
        self.collection_name = collection_name
        self.overrides: typing.Dict[str, Override] = {}

    def __getitem__(self, override_id: str) -> Override:
        """
        Get or create an Override object for a given override_id.

        Args:
            override_id (str): The ID of the override.

        Returns:
            Override: The Override object for the given ID.
        """
        if not self.overrides.get(override_id):
            self.overrides[override_id] = Override(
                self.api_call,
                self.collection_name,
                override_id,
            )
        return self.overrides[override_id]

    def upsert(
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
        response: OverrideSchema = self.api_call.put(
            endpoint=self._endpoint_path(override_id),
            entity_type=OverrideSchema,
            body=schema,
        )
        return response

    def retrieve(self) -> OverrideRetrieveSchema:
        """
        Retrieve all overrides for the collection.

        Returns:
            OverrideRetrieveSchema: The schema containing all overrides.
        """
        response: OverrideRetrieveSchema = self.api_call.get(
            self._endpoint_path(),
            entity_type=OverrideRetrieveSchema,
            as_json=True,
        )
        return response

    @warn_deprecation(
        "SyncOverrides is deprecated on v30+. Use client.curation_sets instead.",
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
        from .collections import Collections

        override_id = override_id or ""

        return "/".join(
            [
                Collections.resource_path,
                self.collection_name,
                Overrides.resource_path,
                override_id,
            ],
        )
