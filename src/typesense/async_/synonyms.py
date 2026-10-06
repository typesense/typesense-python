"""
This module provides async functionality for managing synonyms in Typesense.

Classes:
    - AsyncSynonyms: Handles async operations related to synonyms within a collection.

Methods:
    - __init__: Initializes the AsyncSynonyms object.
    - __getitem__: Retrieves or creates an AsyncSynonym object for a given synonym_id.
    - _endpoint_path: Constructs the API endpoint path for synonym operations.
    - upsert: Creates or updates a synonym.
    - retrieve: Retrieves all synonyms for the collection.

Attributes:
    - RESOURCE_PATH: The API resource path for synonyms.

The AsyncSynonyms class interacts with the Typesense API to manage synonym operations
within a specific collection. It provides methods to create, update, and retrieve
synonyms, as well as access individual AsyncSynonym objects.

For more information regarding Synonyms, refer to the Synonyms [documentation]
(https://typesense.org/docs/27.0/api/synonyms.html#synonyms).

This module uses type hinting and is compatible with Python 3.11+ as well as earlier
versions through the use of the typing_extensions library.
"""

import sys

from typing_extensions import deprecated

from .api_call import AsyncApiCall
from .synonym import AsyncSynonym
from typesense.logger import warn_deprecation
from typesense.types.synonym import (
    SynonymCreateSchema,
    SynonymSchema,
    SynonymsRetrieveSchema,
)

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing


@deprecated("AsyncSynonyms is deprecated on v30+. Use client.synonym_sets instead.")
class AsyncSynonyms:
    """
    Class for managing synonyms in a Typesense collection (async).

    This class provides methods to interact with synonyms, including
    retrieving, creating, and updating them.

    Attributes:
        RESOURCE_PATH (str): The API resource path for synonyms.
        api_call (AsyncApiCall): The API call object for making requests.
        collection_name (str): The name of the collection.
        synonyms (Dict[str, AsyncSynonym]): A dictionary of AsyncSynonym objects.
    """

    resource_path: typing.Final[str] = "synonyms"

    def __init__(self, api_call: AsyncApiCall, collection_name: str) -> None:
        """
        Initialize the AsyncSynonyms object.

        Args:
            api_call (AsyncApiCall): The API call object for making requests.
            collection_name (str): The name of the collection.
        """
        self.api_call = api_call
        self.collection_name = collection_name
        self.synonyms: typing.Dict[str, AsyncSynonym] = {}

    def __getitem__(self, synonym_id: str) -> AsyncSynonym:
        """
        Get or create an AsyncSynonym object for a given synonym_id.

        Args:
            synonym_id (str): The ID of the synonym.

        Returns:
            AsyncSynonym: The AsyncSynonym object for the given ID.
        """
        if not self.synonyms.get(synonym_id):
            self.synonyms[synonym_id] = AsyncSynonym(
                self.api_call,
                self.collection_name,
                synonym_id,
            )
        return self.synonyms[synonym_id]

    async def upsert(
        self, synonym_id: str, schema: SynonymCreateSchema
    ) -> SynonymSchema:
        """
        Create or update a synonym.

        Args:
            id (str): The ID of the synonym.
            schema (SynonymCreateSchema): The schema for creating or updating the synonym.

        Returns:
            SynonymSchema: The created or updated synonym.
        """
        response = await self.api_call.put(
            self._endpoint_path(synonym_id),
            body=schema,
            entity_type=SynonymSchema,
        )
        return response

    async def retrieve(self) -> SynonymsRetrieveSchema:
        """
        Retrieve all synonyms for the collection.

        Returns:
            SynonymsRetrieveSchema: The schema containing all synonyms.
        """
        response = await self.api_call.get(
            self._endpoint_path(),
            entity_type=SynonymsRetrieveSchema,
        )
        return response

    @warn_deprecation(
        "The synonyms API (collections/{collection}/synonyms) is deprecated is removed on v30+. "
        "Use synonym sets (synonym_sets) instead.",
        flag_name="synonyms_deprecation",
    )
    def _endpoint_path(self, synonym_id: typing.Union[str, None] = None) -> str:
        """
        Construct the API endpoint path for synonym operations.

        Args:
            synonym_id (Union[str, None], optional): The ID of the synonym. Defaults to None.

        Returns:
            str: The constructed endpoint path.
        """
        from .collections import AsyncCollections

        synonym_id = synonym_id or ""
        return "/".join(
            [
                AsyncCollections.resource_path,
                self.collection_name,
                AsyncSynonyms.resource_path,
                synonym_id,
            ],
        )
