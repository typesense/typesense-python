"""
This module provides async functionality for managing a single curation set item in Typesense.

Classes:
    AsyncCurationSetItem: Retrieves, upserts and deletes one item of a curation set (async).
"""

from .api_call import AsyncApiCall
from typesense.types.curation_set import (
    CurationItemCreateSchema,
    CurationItemDeleteSchema,
    CurationItemSchema,
)


class AsyncCurationSetItem:
    """
    Manages a single item of a curation set in the Typesense API (async).

    Attributes:
        api_call (AsyncApiCall): The AsyncApiCall instance for making async API requests.
        curation_set_name (str): The name of the curation set.
        item_id (str): The ID of the item.
    """

    def __init__(
        self, api_call: AsyncApiCall, curation_set_name: str, item_id: str
    ) -> None:
        self.api_call = api_call
        self.curation_set_name = curation_set_name
        self.item_id = item_id

    @property
    def _endpoint_path(self) -> str:
        from .curation_sets import AsyncCurationSets

        return "/".join(
            [
                AsyncCurationSets.resource_path,
                self.curation_set_name,
                "items",
                self.item_id,
            ]
        )

    async def retrieve(self) -> CurationItemSchema:
        """
        Retrieve this item.

        Returns:
            CurationItemSchema: The item schema.
        """
        response: CurationItemSchema = await self.api_call.get(
            self._endpoint_path,
            as_json=True,
            entity_type=CurationItemSchema,
        )
        return response

    async def upsert(self, item: CurationItemCreateSchema) -> CurationItemSchema:
        """
        Create or update this item.

        Args:
            item (CurationItemCreateSchema): The item schema.

        Returns:
            CurationItemSchema: The created or updated item.
        """
        response: CurationItemSchema = await self.api_call.put(
            self._endpoint_path,
            body=item,
            entity_type=CurationItemSchema,
        )
        return response

    async def delete(self) -> CurationItemDeleteSchema:
        """
        Delete this item.

        Returns:
            CurationItemDeleteSchema: The deletion response.
        """
        response: CurationItemDeleteSchema = await self.api_call.delete(
            self._endpoint_path,
            entity_type=CurationItemDeleteSchema,
        )
        return response
