import sys

from typesense.api_call import ApiCall
from typesense.configuration import Configuration
from typesense.types.collection import CollectionSchema
from typesense.types.document import (
    DeleteQueryParameters,
    DirtyValuesParameters,
    DocumentSchema,
    DocumentWriteParameters,
)

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

TDoc = typing.TypeVar("TDoc", bound=DocumentSchema)


class Document(typing.Generic[TDoc]):
    def __init__(
        self, api_call: ApiCall, collection_name: str, document_id: str
    ) -> None:
        self.api_call = api_call
        self.collection_name = collection_name
        self.document_id = document_id

    @property
    def _endpoint_path(self) -> str:
        from .collections import Collections
        from .documents import Documents

        return "{0}/{1}/{2}/{3}".format(
            Collections.RESOURCE_PATH,
            self.collection_name,
            Documents.RESOURCE_PATH,
            self.document_id,
        )

    def retrieve(self) -> TDoc:
        response = self.api_call.get(
            endpoint=self._endpoint_path,
            entity_type=typing.Dict[str, str],
            as_json=True,
        )

        return typing.cast(TDoc, response)

    def update(
        self, document: TDoc, params: typing.Union[DirtyValuesParameters, None] = None
    ) -> TDoc:
        response = self.api_call.patch(
            self._endpoint_path,
            body=document,
            params=params,
            entity_type=typing.Dict[str, str],
        )

        return typing.cast(TDoc, response)

    def delete(self) -> TDoc:
        response = self.api_call.delete(
            self._endpoint_path, entity_type=typing.Dict[str, str]
        )
        return typing.cast(TDoc, response)
