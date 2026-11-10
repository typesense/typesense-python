"""Client for single Synonym Set item operations (async)."""

from .api_call import ApiCall
from typesense.types.synonym_set import (
    SynonymItemDeleteSchema,
    SynonymItemSchema,
    SynonymItemUpsertSchema,
)


class SynonymSetItem:
    def __init__(
        self, api_call: ApiCall, synonym_set_name: str, item_id: str
    ) -> None:
        self.api_call = api_call
        self.synonym_set_name = synonym_set_name
        self.item_id = item_id

    @property
    def _endpoint_path(self) -> str:
        from .synonym_sets import SynonymSets

        return "/".join(
            [
                SynonymSets.resource_path,
                self.synonym_set_name,
                "items",
                self.item_id,
            ]
        )

    def retrieve(self) -> SynonymItemSchema:
        response: SynonymItemSchema = self.api_call.get(
            self._endpoint_path,
            as_json=True,
            entity_type=SynonymItemSchema,
        )
        return response

    def upsert(self, item: SynonymItemUpsertSchema) -> SynonymItemSchema:
        response: SynonymItemSchema = self.api_call.put(
            self._endpoint_path,
            body=item,
            entity_type=SynonymItemSchema,
        )
        return response

    def delete(self) -> SynonymItemDeleteSchema:
        response: SynonymItemDeleteSchema = self.api_call.delete(
            self._endpoint_path,
            entity_type=SynonymItemDeleteSchema,
        )
        return response
