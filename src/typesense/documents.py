# mypy: disable-error-code="misc"
import json
import sys

from typesense.api_call import ApiCall
from typesense.exceptions import TypesenseClientError
from typesense.types.document import (
    DeleteQueryParameters,
    DeleteResponse,
    DirtyValuesParameters,
    DocumentExportParameters,
    DocumentImportParameters,
    DocumentImportParametersReturnDoc,
    DocumentImportParametersReturnDocAndId,
    DocumentImportParametersReturnId,
    DocumentSchema,
    DocumentWriteParameters,
    ImportResponse,
    ImportResponseFail,
    ImportResponseSuccess,
    ImportResponseWithDoc,
    ImportResponseWithDocAndId,
    ImportResponseWithId,
    SearchParameters,
    SearchResponse,
    UpdateByFilterParameters,
    UpdateByFilterResponse,
)

from .document import Document
from .logger import logger
from .preprocess import stringify_search_params
from .validation import validate_search

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

TDoc = typing.TypeVar("TDoc", bound=DocumentSchema)


class Documents(typing.Generic[TDoc]):
    RESOURCE_PATH = "documents"

    def __init__(self, api_call: ApiCall, collection_name: str) -> None:
        self.api_call = api_call
        self.collection_name = collection_name
        self.documents: typing.Dict[str, Document[TDoc]] = {}

    def __getitem__(self, document_id: str) -> Document[TDoc]:
        if document_id not in self.documents:
            self.documents[document_id] = Document(
                self.api_call, self.collection_name, document_id
            )

        return self.documents[document_id]

    def _endpoint_path(self, action: typing.Union[str, None] = None) -> str:
        from .collections import Collections

        action = action or ""
        return "{0}/{1}/{2}/{3}".format(
            Collections.RESOURCE_PATH,
            self.collection_name,
            Documents.RESOURCE_PATH,
            action,
        )

    def create(
        self, document: TDoc, params: typing.Union[DirtyValuesParameters, None] = None
    ) -> TDoc:
        params = params or {}
        params["action"] = "create"
        response = self.api_call.post(
            self._endpoint_path(),
            body=document,
            params=params,
            as_json=True,
            entity_type=typing.Dict[str, str],
        )
        return typing.cast(TDoc, response)

    def create_many(
        self,
        documents: typing.List[TDoc],
        params: typing.Union[DirtyValuesParameters, None] = None,
    ) -> typing.List[typing.Union[ImportResponseSuccess, ImportResponseFail[TDoc]]]:
        logger.warning("`create_many` is deprecated: please use `import_`.")
        return self.import_(documents, params)

    def upsert(
        self, document: TDoc, params: typing.Union[DirtyValuesParameters, None] = None
    ) -> TDoc:
        params = params or {}
        params["action"] = "upsert"
        response = self.api_call.post(
            self._endpoint_path(),
            body=document,
            params=params,
            as_json=True,
            entity_type=typing.Dict[str, str],
        )
        return typing.cast(TDoc, response)

    def update(
        self,
        document: TDoc,
        params: typing.Union[UpdateByFilterParameters, None] = None,
    ) -> UpdateByFilterResponse:
        params = params or {}
        params["action"] = "update"
        response: UpdateByFilterResponse = self.api_call.patch(
            self._endpoint_path(),
            body=document,
            params=params,
            entity_type=UpdateByFilterResponse,
        )
        return response

    def import_jsonl(self, documents_jsonl: str) -> str:
        logger.warning("`import_jsonl` is deprecated: please use `import_`.")
        return self.import_(documents_jsonl)

    @typing.overload
    def import_(
        self,
        documents: typing.List[TDoc],
        params: DocumentImportParametersReturnDocAndId,
        batch_size: typing.Union[int, None] = None,
    ) -> typing.List[
        typing.Union[ImportResponseWithDocAndId[TDoc], ImportResponseFail[TDoc]]
    ]: ...

    @typing.overload
    def import_(
        self,
        documents: typing.List[TDoc],
        params: DocumentImportParametersReturnId,
        batch_size: typing.Union[int, None] = None,
    ) -> typing.List[typing.Union[ImportResponseWithId, ImportResponseFail[TDoc]]]: ...

    @typing.overload
    def import_(
        self,
        documents: typing.List[TDoc],
        params: typing.Union[DocumentWriteParameters, None] = None,
        batch_size: typing.Union[int, None] = None,
    ) -> typing.List[typing.Union[ImportResponseSuccess, ImportResponseFail[TDoc]]]: ...

    @typing.overload
    def import_(
        self,
        documents: typing.List[TDoc],
        params: DocumentImportParametersReturnDoc,
        batch_size: typing.Union[int, None] = None,
    ) -> typing.List[
        typing.Union[ImportResponseWithDoc[TDoc], ImportResponseFail[TDoc]]
    ]: ...

    @typing.overload
    def import_(
        self,
        documents: typing.List[TDoc],
        params: typing.Union[
            DocumentImportParameters,
            None,
        ],
        batch_size: typing.Union[int, None] = None,
    ) -> typing.List[ImportResponse[TDoc]]: ...

    @typing.overload
    def import_(
        self,
        documents: typing.Union[bytes, str],
        params: typing.Union[
            DocumentImportParameters,
            None,
        ] = None,
        batch_size: typing.Union[int, None] = None,
    ) -> str: ...

    # Actual implementation that matches the overloads
    def import_(
        self,
        documents: typing.Union[bytes, str, typing.List[TDoc]],
        params: typing.Union[
            DocumentImportParameters,
            None,
        ] = None,
        batch_size: typing.Union[int, None] = None,
    ) -> typing.Union[
        ImportResponse[TDoc],
        str,
    ]:
        if not isinstance(documents, (str, bytes)):
            if batch_size:
                response_objs: ImportResponse[TDoc] = []
                batch: typing.List[TDoc] = []
                for document in documents:
                    batch.append(document)
                    if len(batch) == batch_size:
                        api_response = self.import_(documents=batch, params=params)
                        response_objs.extend(api_response)
                        batch = []
                if batch:
                    api_response = self.import_(batch, params)
                    response_objs.extend(api_response)

            else:
                document_strs: typing.List[str] = []
                for document in documents:
                    document_strs.append(json.dumps(document))

                if len(document_strs) == 0:
                    raise TypesenseClientError(
                        f"Cannot import an empty list of documents."
                    )

                docs_import = "\n".join(document_strs)
                res = self.api_call.post(
                    self._endpoint_path("import"),
                    body=docs_import,
                    params=params,
                    entity_type=str,
                    as_json=False,
                )
                res_obj_strs = res.split("\n")

                response_objs = []
                for res_obj_str in res_obj_strs:
                    try:
                        res_obj_json: typing.Union[
                            ImportResponseWithDocAndId[TDoc],
                            ImportResponseWithDoc[TDoc],
                            ImportResponseWithId,
                            ImportResponseSuccess,
                            ImportResponseFail[TDoc],
                        ] = json.loads(res_obj_str)
                    except json.JSONDecodeError as e:
                        raise TypesenseClientError(
                            f"Invalid response - {res_obj_str}"
                        ) from e
                    response_objs.append(res_obj_json)

            return response_objs
        else:
            api_response = self.api_call.post(
                self._endpoint_path("import"),
                body=documents,
                params=params,
                as_json=False,
                entity_type=str,
            )
            return api_response

    def export(
        self, params: typing.Union[DocumentExportParameters, None] = None
    ) -> str:
        api_response: str = self.api_call.get(
            self._endpoint_path("export"), params=params, as_json=False, entity_type=str
        )
        return api_response

    def search(self, search_parameters: SearchParameters) -> SearchResponse[TDoc]:
        stringified_search_params = stringify_search_params(search_parameters)
        response: SearchResponse[TDoc] = self.api_call.get(
            self._endpoint_path("search"),
            params=stringified_search_params,
            entity_type=SearchResponse,
            as_json=True,
        )
        return response

    def delete(
        self, params: typing.Union[DeleteQueryParameters, None] = None
    ) -> DeleteResponse:
        response: DeleteResponse = self.api_call.delete(
            self._endpoint_path(), params=params, entity_type=DeleteResponse
        )
        return response
