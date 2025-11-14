"""Client for single Curation Set operations, including items APIs."""

import sys

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

from typesense.api_call import ApiCall
from typesense.types.curation_set import (
    CurationItemDeleteSchema,
    CurationItemSchema,
    CurationSetDeleteSchema,
    CurationSetListItemResponseSchema,
    CurationSetSchema,
    CurationSetUpsertSchema,
)


class CurationSet:
    def __init__(self, api_call: ApiCall, name: str) -> None:
        self.api_call = api_call
        self.name = name

    @property
    def _endpoint_path(self) -> str:
        from typesense.curation_sets import CurationSets

        return "/".join([CurationSets.resource_path, self.name])

    def retrieve(self) -> CurationSetSchema:
        response: CurationSetSchema = self.api_call.get(
            self._endpoint_path,
            as_json=True,
            entity_type=CurationSetSchema,
        )
        return response

    def delete(self) -> CurationSetDeleteSchema:
        response: CurationSetDeleteSchema = self.api_call.delete(
            self._endpoint_path,
            entity_type=CurationSetDeleteSchema,
        )
        return response

    def upsert(
        self,
        payload: CurationSetUpsertSchema,
    ) -> CurationSetSchema:
        response: CurationSetSchema = self.api_call.put(
            "/".join([self._endpoint_path]),
            body=payload,
            entity_type=CurationSetSchema,
        )
        return response

    # Items sub-resource
    @property
    def _items_path(self) -> str:
        return "/".join([self._endpoint_path, "items"])  # /curation_sets/{name}/items

    def list_items(
        self,
        *,
        limit: typing.Union[int, None] = None,
        offset: typing.Union[int, None] = None,
    ) -> CurationSetListItemResponseSchema:
        params: typing.Dict[str, typing.Union[int, None]] = {
            "limit": limit,
            "offset": offset,
        }
        # Filter out None values to avoid sending them
        clean_params: typing.Dict[str, int] = {
            k: v for k, v in params.items() if v is not None
        }
        response: CurationSetListItemResponseSchema = self.api_call.get(
            self._items_path,
            as_json=True,
            entity_type=CurationSetListItemResponseSchema,
            params=clean_params or None,
        )
        return response

    def get_item(self, item_id: str) -> CurationItemSchema:
        response: CurationItemSchema = self.api_call.get(
            "/".join([self._items_path, item_id]),
            as_json=True,
            entity_type=CurationItemSchema,
        )
        return response

    def upsert_item(self, item_id: str, item: CurationItemSchema) -> CurationItemSchema:
        response: CurationItemSchema = self.api_call.put(
            "/".join([self._items_path, item_id]),
            body=item,
            entity_type=CurationItemSchema,
        )
        return response

    def delete_item(self, item_id: str) -> CurationItemDeleteSchema:
        response: CurationItemDeleteSchema = self.api_call.delete(
            "/".join([self._items_path, item_id]),
            entity_type=CurationItemDeleteSchema,
        )
        return response
