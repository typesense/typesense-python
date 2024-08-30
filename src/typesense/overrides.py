from __future__ import annotations

import sys

from typesense.api_call import ApiCall
from typesense.types.override import (
    OverrideCreateSchema,
    OverrideRetrieveSchema,
    OverrideSchema,
)

from .override import Override

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing


class Overrides(object):
    RESOURCE_PATH = 'overrides'

    def __init__(
        self,
        api_call: ApiCall,
        collection_name: str,
    ) -> None:
        self.api_call = api_call
        self.collection_name = collection_name
        self.overrides: typing.Dict[str, Override] = {}

    def __getitem__(self, override_id: str) -> Override:
        if not self.overrides.get(override_id):
            self.overrides[override_id] = Override(
                self.api_call, self.collection_name, override_id
            )
        return self.overrides[override_id]

    def _endpoint_path(self, override_id: typing.Union[str, None] = None) -> str:
        from .collections import Collections

        override_id = override_id or ""
        return "{0}/{1}/{2}/{3}".format(
            Collections.RESOURCE_PATH,
            self.collection_name,
            Overrides.RESOURCE_PATH,
            override_id,
        )

    def upsert(self, id: str, schema: OverrideCreateSchema) -> OverrideSchema:
        response: OverrideSchema = self.api_call.put(
            endpoint=self._endpoint_path(id),
            entity_type=OverrideSchema,
            body=schema,
        )
        return response

    def retrieve(self) -> OverrideRetrieveSchema:
        response: OverrideRetrieveSchema = self.api_call.get(
            self._endpoint_path(), entity_type=OverrideRetrieveSchema, as_json=True
        )
        return response
