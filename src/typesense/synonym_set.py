"""Client for single Synonym Set operations."""

import sys

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

from typesense.api_call import ApiCall
from typesense.types.synonym_set import (
    SynonymSetDeleteSchema,
    SynonymSetRetrieveSchema,
)


class SynonymSet:
    def __init__(self, api_call: ApiCall, name: str) -> None:
        self.api_call = api_call
        self.name = name

    @property
    def _endpoint_path(self) -> str:
        from typesense.synonym_sets import SynonymSets

        return "/".join([SynonymSets.resource_path, self.name])

    def retrieve(self) -> SynonymSetRetrieveSchema:
        response: SynonymSetRetrieveSchema = self.api_call.get(
            self._endpoint_path,
            as_json=True,
            entity_type=SynonymSetRetrieveSchema,
        )
        return response

    def delete(self) -> SynonymSetDeleteSchema:
        response: SynonymSetDeleteSchema = self.api_call.delete(
            self._endpoint_path,
            entity_type=SynonymSetDeleteSchema,
        )
        return response


