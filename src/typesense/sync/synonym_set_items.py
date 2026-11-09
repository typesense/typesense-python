"""Client for Synonym Set items collection operations (async)."""

import sys

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

from .api_call import ApiCall
from .synonym_set_item import SynonymSetItem
from typesense.types.synonym_set import SynonymItemSchema, SynonymItemUpsertSchema


class SynonymSetItems:
    def __init__(self, api_call: ApiCall, synonym_set_name: str) -> None:
        self.api_call = api_call
        self.synonym_set_name = synonym_set_name

    def __getitem__(self, item_id: str) -> SynonymSetItem:
        return SynonymSetItem(self.api_call, self.synonym_set_name, item_id)

    @property
    def _endpoint_path(self) -> str:
        from .synonym_sets import SynonymSets

        return "/".join(
            [SynonymSets.resource_path, self.synonym_set_name, "items"]
        )

    def retrieve(
        self,
        *,
        limit: typing.Union[int, None] = None,
        offset: typing.Union[int, None] = None,
    ) -> typing.List[SynonymItemSchema]:
        params: typing.Dict[str, typing.Union[int, None]] = {
            "limit": limit,
            "offset": offset,
        }
        clean_params: typing.Dict[str, int] = {
            k: v for k, v in params.items() if v is not None
        }
        response: typing.List[SynonymItemSchema] = self.api_call.get(
            self._endpoint_path,
            as_json=True,
            entity_type=typing.List[SynonymItemSchema],
            params=clean_params or None,
        )
        return response

    def upsert(
        self, item_id: str, item: SynonymItemUpsertSchema
    ) -> SynonymItemSchema:
        return self[item_id].upsert(item)
