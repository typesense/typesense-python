"""Client for single Synonym Set operations (async)."""

import sys

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

from .api_call import ApiCall
from .synonym_set_items import SynonymSetItems
from typesense.types.synonym_set import (
    SynonymItemDeleteSchema,
    SynonymItemSchema,
    SynonymItemUpsertSchema,
    SynonymSetCreateSchema,
    SynonymSetDeleteSchema,
    SynonymSetRetrieveSchema,
)


class SynonymSet:
    def __init__(self, api_call: ApiCall, name: str) -> None:
        self.api_call = api_call
        self.name = name
        self.items = SynonymSetItems(api_call, name)

    @property
    def _endpoint_path(self) -> str:
        from .synonym_sets import SynonymSets

        return "/".join([SynonymSets.resource_path, self.name])

    def retrieve(self) -> SynonymSetRetrieveSchema:
        response: SynonymSetRetrieveSchema = self.api_call.get(
            self._endpoint_path,
            as_json=True,
            entity_type=SynonymSetRetrieveSchema,
        )
        return response

    def upsert(self, set: SynonymSetCreateSchema) -> SynonymSetCreateSchema:
        response: SynonymSetCreateSchema = self.api_call.put(
            self._endpoint_path,
            entity_type=SynonymSetCreateSchema,
            body=set,
        )
        return response

    def delete(self) -> SynonymSetDeleteSchema:
        response: SynonymSetDeleteSchema = self.api_call.delete(
            self._endpoint_path,
            entity_type=SynonymSetDeleteSchema,
        )
        return response

    def list_items(
        self,
        *,
        limit: typing.Union[int, None] = None,
        offset: typing.Union[int, None] = None,
    ) -> typing.List[SynonymItemSchema]:
        return self.items.retrieve(limit=limit, offset=offset)

    def get_item(self, item_id: str) -> SynonymItemSchema:
        return self.items[item_id].retrieve()

    def upsert_item(
        self,
        item_id: str,
        item: typing.Union[SynonymItemSchema, SynonymItemUpsertSchema],
    ) -> SynonymItemSchema:
        return self.items[item_id].upsert(item)

    def delete_item(self, item_id: str) -> SynonymItemDeleteSchema:
        return self.items[item_id].delete()
