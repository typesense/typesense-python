"""
This module provides async functionality for managing the items of a curation set in Typesense.

Classes:
    AsyncCurationSetItems: Lists, upserts and accesses items of a single curation set (async).
"""

import sys

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

from .api_call import AsyncApiCall
from .curation_set_item import AsyncCurationSetItem
from typesense.types.curation_set import (
    CurationItemCreateSchema,
    CurationItemSchema,
    CurationSetListItemResponseSchema,
)


class AsyncCurationSetItems:
    """
    Manages the items of a single curation set in the Typesense API (async).

    Attributes:
        api_call (AsyncApiCall): The AsyncApiCall instance for making async API requests.
        curation_set_name (str): The name of the curation set.
    """

    def __init__(self, api_call: AsyncApiCall, curation_set_name: str) -> None:
        self.api_call = api_call
        self.curation_set_name = curation_set_name

    def __getitem__(self, item_id: str) -> AsyncCurationSetItem:
        """
        Get an AsyncCurationSetItem instance for a given item ID.

        Example:
            >>> item = curation_sets["products"].items["rule-1"]
        """
        return AsyncCurationSetItem(self.api_call, self.curation_set_name, item_id)

    @property
    def _endpoint_path(self) -> str:
        from .curation_sets import AsyncCurationSets

        return "/".join(
            [AsyncCurationSets.resource_path, self.curation_set_name, "items"]
        )

    async def retrieve(
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
        response: CurationSetListItemResponseSchema = await self.api_call.get(
            self._endpoint_path,
            as_json=True,
            entity_type=CurationSetListItemResponseSchema,
            params=clean_params or None,
        )
        return response

    async def upsert(
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
        return await self[item_id].upsert(item)
