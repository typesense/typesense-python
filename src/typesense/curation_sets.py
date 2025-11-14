"""Client for Curation Sets collection operations."""

import sys

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

from typesense.api_call import ApiCall
from typesense.curation_set import CurationSet
from typesense.types.curation_set import (
    CurationSetsListResponseSchema,
)


class CurationSets:
    resource_path: typing.Final[str] = "/curation_sets"

    def __init__(self, api_call: ApiCall) -> None:
        self.api_call = api_call

    def retrieve(self) -> CurationSetsListResponseSchema:
        response: CurationSetsListResponseSchema = self.api_call.get(
            CurationSets.resource_path,
            as_json=True,
            entity_type=CurationSetsListResponseSchema,
        )
        return response

    def __getitem__(self, curation_set_name: str) -> CurationSet:
        from typesense.curation_set import CurationSet as PerSet

        return PerSet(self.api_call, curation_set_name)
