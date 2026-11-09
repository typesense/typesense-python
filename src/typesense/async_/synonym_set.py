"""Client for single Synonym Set operations (async)."""

import sys

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

from .api_call import AsyncApiCall
from .synonym_set_items import AsyncSynonymSetItems
from typesense.types.synonym_set import (
    SynonymItemDeleteSchema,
    SynonymItemSchema,
    SynonymItemUpsertSchema,
    SynonymSetCreateSchema,
    SynonymSetDeleteSchema,
    SynonymSetRetrieveSchema,
)


class AsyncSynonymSet:
    def __init__(self, api_call: AsyncApiCall, name: str) -> None:
        self.api_call = api_call
        self.name = name
        self.items = AsyncSynonymSetItems(api_call, name)

    @property
    def _endpoint_path(self) -> str:
        from .synonym_sets import AsyncSynonymSets

        return "/".join([AsyncSynonymSets.resource_path, self.name])

    async def retrieve(self) -> SynonymSetRetrieveSchema:
        response: SynonymSetRetrieveSchema = await self.api_call.get(
            self._endpoint_path,
            as_json=True,
            entity_type=SynonymSetRetrieveSchema,
        )
        return response

    async def upsert(self, set: SynonymSetCreateSchema) -> SynonymSetCreateSchema:
        response: SynonymSetCreateSchema = await self.api_call.put(
            self._endpoint_path,
            entity_type=SynonymSetCreateSchema,
            body=set,
        )
        return response

    async def delete(self) -> SynonymSetDeleteSchema:
        response: SynonymSetDeleteSchema = await self.api_call.delete(
            self._endpoint_path,
            entity_type=SynonymSetDeleteSchema,
        )
        return response

    async def list_items(
        self,
        *,
        limit: typing.Union[int, None] = None,
        offset: typing.Union[int, None] = None,
    ) -> typing.List[SynonymItemSchema]:
        return await self.items.retrieve(limit=limit, offset=offset)

    async def get_item(self, item_id: str) -> SynonymItemSchema:
        return await self.items[item_id].retrieve()

    async def upsert_item(
        self,
        item_id: str,
        item: typing.Union[SynonymItemSchema, SynonymItemUpsertSchema],
    ) -> SynonymItemSchema:
        return await self.items[item_id].upsert(item)

    async def delete_item(self, item_id: str) -> SynonymItemDeleteSchema:
        return await self.items[item_id].delete()
