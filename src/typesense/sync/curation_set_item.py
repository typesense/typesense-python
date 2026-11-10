"""
This module provides async functionality for managing a single curation set item in Typesense.

Classes:
    CurationSetItem: Retrieves, upserts and deletes one item of a curation set (async).
"""

from .api_call import ApiCall
from typesense.types.curation_set import (
    CurationItemCreateSchema,
    CurationItemDeleteSchema,
    CurationItemSchema,
)


class CurationSetItem:
    """
    Manages a single item of a curation set in the Typesense API (async).

    Attributes:
        api_call (ApiCall): The ApiCall instance for making async API requests.
        curation_set_name (str): The name of the curation set.
        item_id (str): The ID of the item.
    """

    def __init__(
        self, api_call: ApiCall, curation_set_name: str, item_id: str
    ) -> None:
        self.api_call = api_call
        self.curation_set_name = curation_set_name
        self.item_id = item_id

    @property
    def _endpoint_path(self) -> str:
        from .curation_sets import CurationSets

        return "/".join(
            [
                CurationSets.resource_path,
                self.curation_set_name,
                "items",
                self.item_id,
            ]
        )

    def retrieve(self) -> CurationItemSchema:
        """
        Retrieve this item.

        Returns:
            CurationItemSchema: The item schema.
        """
        response: CurationItemSchema = self.api_call.get(
            self._endpoint_path,
            as_json=True,
            entity_type=CurationItemSchema,
        )
        return response

    def upsert(self, item: CurationItemCreateSchema) -> CurationItemSchema:
        """
        Create or update this item.

        Args:
            item (CurationItemCreateSchema): The item schema.

        Returns:
            CurationItemSchema: The created or updated item.
        """
        response: CurationItemSchema = self.api_call.put(
            self._endpoint_path,
            body=item,
            entity_type=CurationItemSchema,
        )
        return response

    def delete(self) -> CurationItemDeleteSchema:
        """
        Delete this item.

        Returns:
            CurationItemDeleteSchema: The deletion response.
        """
        response: CurationItemDeleteSchema = self.api_call.delete(
            self._endpoint_path,
            entity_type=CurationItemDeleteSchema,
        )
        return response
