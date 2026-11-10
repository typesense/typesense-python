"""
This module provides async functionality for managing the items of a curation set in Typesense.

Classes:
    CurationSetItems: Lists, upserts and accesses items of a single curation set (async).
"""

import sys

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

from .api_call import ApiCall
from .curation_set_item import CurationSetItem
from typesense.types.curation_set import (
    CurationItemCreateSchema,
    CurationItemSchema,
    CurationSetListItemResponseSchema,
)


class CurationSetItems:
    """
    Manages the items of a single curation set in the Typesense API (async).

    Attributes:
        api_call (ApiCall): The ApiCall instance for making async API requests.
        curation_set_name (str): The name of the curation set.
    """

    def __init__(self, api_call: ApiCall, curation_set_name: str) -> None:
        self.api_call = api_call
        self.curation_set_name = curation_set_name

    def __getitem__(self, item_id: str) -> CurationSetItem:
        """
        Get an CurationSetItem instance for a given item ID.

        Example:
            >>> item = curation_sets["products"].items["rule-1"]
        """
        return CurationSetItem(self.api_call, self.curation_set_name, item_id)

    @property
    def _endpoint_path(self) -> str:
        from .curation_sets import CurationSets

        return "/".join(
            [CurationSets.resource_path, self.curation_set_name, "items"]
        )

    def retrieve(
        self,
        *,
        limit: typing.Union[int, None] = None,
        offset: typing.Union[int, None] = None,
    ) -> CurationSetListItemResponseSchema:
        """
        List items in this curation set.

        Args:
            limit (Union[int, None], optional): Maximum number of items to return. Defaults to None.
            offset (Union[int, None], optional): Number of items to skip. Defaults to None.

        Returns:
            CurationSetListItemResponseSchema: The list of items in the curation set.
        """
        params: typing.Dict[str, typing.Union[int, None]] = {
            "limit": limit,
            "offset": offset,
        }
        clean_params: typing.Dict[str, int] = {
            k: v for k, v in params.items() if v is not None
        }
        response: CurationSetListItemResponseSchema = self.api_call.get(
            self._endpoint_path,
            as_json=True,
            entity_type=CurationSetListItemResponseSchema,
            params=clean_params or None,
        )
        return response

    def upsert(
        self, item_id: str, item: CurationItemCreateSchema
    ) -> CurationItemSchema:
        """
        Create or update an item in this curation set.

        Args:
            item_id (str): The ID of the item.
            item (CurationItemCreateSchema): The item schema.

        Returns:
            CurationItemSchema: The created or updated item.
        """
        return self[item_id].upsert(item)
