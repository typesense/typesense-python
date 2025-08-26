"""Client for Synonym Sets collection operations."""

import sys

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

from typesense.api_call import ApiCall
from typesense.types.synonym_set import (
    SynonymSetCreateSchema,
    SynonymSetDeleteSchema,
    SynonymSetRetrieveSchema,
    SynonymSetSchema,
)


class SynonymSets:
    resource_path: typing.Final[str] = "/synonym_sets"

    def __init__(self, api_call: ApiCall) -> None:
        self.api_call = api_call

    def retrieve(self) -> typing.List[SynonymSetSchema]:
        response: typing.List[SynonymSetSchema] = self.api_call.get(
            SynonymSets.resource_path,
            as_json=True,
            entity_type=typing.List[SynonymSetSchema],
        )
        return response

    def __getitem__(self, synonym_set_name: str) -> "SynonymSet":
        from typesense.synonym_set import SynonymSet as PerSet

        return PerSet(self.api_call, synonym_set_name)

    def upsert(
        self,
        synonym_set_name: str,
        payload: SynonymSetCreateSchema,
    ) -> SynonymSetSchema:
        response: SynonymSetSchema = self.api_call.put(
            "/".join([SynonymSets.resource_path, synonym_set_name]),
            body=payload,
            entity_type=SynonymSetSchema,
        )
        return response


