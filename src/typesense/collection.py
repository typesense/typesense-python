from __future__ import annotations

import sys

from typesense.types.collection import CollectionSchema, CollectionUpdateSchema

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

from typesense.api_call import ApiCall
from typesense.types.document import DocumentSchema

from .documents import Documents
from .overrides import Overrides
from .synonyms import Synonyms

TDoc = typing.TypeVar("TDoc", bound=DocumentSchema)


class Collection(typing.Generic[TDoc]):
    def __init__(self, api_call: ApiCall, name: str):
        self.name = name
        self.api_call = api_call
        self.documents = Documents[TDoc](api_call, name)
        self.overrides = Overrides(api_call, name)
        self.synonyms = Synonyms(api_call, name)

    @property
    def _endpoint_path(self) -> str:
        from typesense.collections import Collections

        return f"{Collections.RESOURCE_PATH}/{self.name}"

    def retrieve(self) -> CollectionSchema:
        response: CollectionSchema = self.api_call.get(
            endpoint=self._endpoint_path, entity_type=CollectionSchema, as_json=True
        )
        return response

    def update(self, schema_change: CollectionUpdateSchema) -> CollectionUpdateSchema:
        response: CollectionUpdateSchema = self.api_call.patch(
            endpoint=self._endpoint_path,
            body=schema_change,
            entity_type=CollectionUpdateSchema,
        )
        return response

    # There's currently no parameters passed to Collection deletions, but ensuring future compatibility
    def delete(
        self,
        params: typing.Union[typing.Dict[str, typing.Union[str, bool]], None] = None,
    ) -> CollectionSchema:
        return self.api_call.delete(
            self._endpoint_path, entity_type=CollectionSchema, params=params
        )
