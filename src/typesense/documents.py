"""
This module provides functionality for managing documents in Typesense collections.

Classes:
    - Documents: Handles operations related to documents within a collection.

Methods:
    - __init__: Initializes the Documents object.
    - __getitem__: Retrieves or creates a Document object for a given document_id.
    - _endpoint_path: Constructs the API endpoint path for document operations.
    - create: Creates a new document in the collection.
    - create_many: (Deprecated) Creates multiple documents in the collection.
    - upsert: Creates or updates a document in the collection.
    - update: Updates a document in the collection.
    - import_jsonl: (Deprecated) Imports documents from a JSONL string.
    - import_: Imports documents into the collection.
    - export: Exports documents from the collection.
    - search: Searches for documents in the collection.
    - delete: Deletes documents from the collection based on given parameters.

Attributes:
    - resource_path: The API resource path for document operations.

The Documents class interacts with the Typesense API to manage document operations
within a specific collection. It provides methods to create, update, import, export,
search, and delete documents.

This module uses type hinting and is compatible with Python 3.11+ as well as earlier
versions through the use of the typing_extensions library.
"""

import json
import sys

from typesense.api_call import ApiCall
from typesense.document import Document
from typesense.exceptions import TypesenseClientError
from typesense.logger import logger
from typesense.preprocess import stringify_search_params
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

# mypy: disable-error-code="misc"


if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

TDoc = typing.TypeVar("TDoc", bound=DocumentSchema)

_ImportParameters = typing.Union[
    DocumentImportParameters,
    None,
]


class Documents(typing.Generic[TDoc]):
    """
    Class for managing documents in a Typesense collection.

    This class provides methods to interact with documents, including
    creating, updating, importing, exporting, searching, and deleting them.

    Attributes:
        resource_path (str): The API resource path for document operations.
        api_call (ApiCall): The API call object for making requests.
        collection_name (str): The name of the collection.
        documents (Dict[str, Document[TDoc]]): A dictionary of Document objects.
    """

    resource_path: typing.Final[str] = "documents"

    def __init__(self, api_call: ApiCall, collection_name: str) -> None:
        """
        Initialize the Documents object.

        Args:
            api_call (ApiCall): The API call object for making requests.
            collection_name (str): The name of the collection.
        """
        self.api_call = api_call
        self.collection_name = collection_name
        self.documents: typing.Dict[str, Document[TDoc]] = {}

    def __getitem__(self, document_id: str) -> Document[TDoc]:
        """
        Get or create a Document object for a given document_id.

        Args:
            document_id (str): The ID of the document.

        Returns:
            Document[TDoc]: The Document object for the given ID.
        """
        if document_id not in self.documents:
            self.documents[document_id] = Document(
                self.api_call,
                self.collection_name,
                document_id,
            )

        return self.documents[document_id]

    def create(
        self,
        document: TDoc,
        dirty_values_parameters: typing.Union[DirtyValuesParameters, None] = None,
    ) -> TDoc:
        """
        Create a new document in the collection.

        Args:
            document (TDoc): The document to create.
            dirty_values_parameters (Union[DirtyValuesParameters, None], optional):
                Parameters for handling dirty values.

        Returns:
            TDoc: The created document.
        """
        dirty_values_parameters = dirty_values_parameters or {}
        dirty_values_parameters["action"] = "create"
        response: TDoc = self.api_call.post(
            self._endpoint_path(),
            body=document,
            params=dirty_values_parameters,
            as_json=True,
            entity_type=typing.Dict[str, str],
        )
        return response

    def create_many(
        self,
        documents: typing.List[TDoc],
        dirty_values_parameters: typing.Union[DirtyValuesParameters, None] = None,
    ) -> typing.List[typing.Union[ImportResponseSuccess, ImportResponseFail[TDoc]]]:
        """
        Create multiple documents in the collection.

        Args:
            documents (List[TDoc]): The list of documents to create.
            dirty_values_parameters (Union[DirtyValuesParameters, None], optional):
                Parameters for handling dirty values.

        Returns:
            List[Union[ImportResponseSuccess, ImportResponseFail[TDoc]]]:
                The list of import responses.
        """
        logger.warn("`create_many` is deprecated: please use `import_`.")
        return self.import_(documents, dirty_values_parameters)

    def upsert(
        self,
        document: TDoc,
        dirty_values_parameters: typing.Union[DirtyValuesParameters, None] = None,
    ) -> TDoc:
        """
        Create or update a document in the collection.

        Args:
            document (TDoc): The document to upsert.
            dirty_values_parameters (Union[DirtyValuesParameters, None], optional):
               Parameters for handling dirty values.

        Returns:
            TDoc: The upserted document.
        """
        dirty_values_parameters = dirty_values_parameters or {}
        dirty_values_parameters["action"] = "upsert"
        response: TDoc = self.api_call.post(
            self._endpoint_path(),
            body=document,
            params=dirty_values_parameters,
            as_json=True,
            entity_type=typing.Dict[str, str],
        )
        return response

    def update(
        self,
        document: TDoc,
        dirty_values_parameters: typing.Union[UpdateByFilterParameters, None] = None,
    ) -> UpdateByFilterResponse:
        """
        Update a document in the collection.

        Args:
            document (TDoc): The document to update.
            dirty_values_parameters (Union[UpdateByFilterParameters, None], optional):
                Parameters for handling dirty values and filtering.

        Returns:
            UpdateByFilterResponse: The response containing information about the update.
        """
        dirty_values_parameters = dirty_values_parameters or {}
        dirty_values_parameters["action"] = "update"
        response: UpdateByFilterResponse = self.api_call.patch(
            self._endpoint_path(),
            body=document,
            params=dirty_values_parameters,
            entity_type=UpdateByFilterResponse,
        )
        return response

    def import_jsonl(self, documents_jsonl: str) -> str:
        """
        Import documents from a JSONL string.

        Args:
            documents_jsonl (str): The JSONL string containing documents to import.

        Returns:
            str: The import response as a string.
        """
        logger.warning("`import_jsonl` is deprecated: please use `import_`.")
        return self.import_(documents_jsonl)

    @typing.overload
    def import_(
        self,
        documents: typing.List[TDoc],
        import_parameters: DocumentImportParametersReturnDocAndId,
        batch_size: typing.Union[int, None] = None,
    ) -> typing.List[
        typing.Union[ImportResponseWithDocAndId[TDoc], ImportResponseFail[TDoc]]
    ]: ...

    @typing.overload
    def import_(
        self,
        documents: typing.List[TDoc],
        import_parameters: DocumentImportParametersReturnId,
        batch_size: typing.Union[int, None] = None,
    ) -> typing.List[typing.Union[ImportResponseWithId, ImportResponseFail[TDoc]]]: ...

    @typing.overload
    def import_(
        self,
        documents: typing.List[TDoc],
        import_parameters: typing.Union[DocumentWriteParameters, None] = None,
        batch_size: typing.Union[int, None] = None,
    ) -> typing.List[typing.Union[ImportResponseSuccess, ImportResponseFail[TDoc]]]: ...

    @typing.overload
    def import_(
        self,
        documents: typing.List[TDoc],
        import_parameters: DocumentImportParametersReturnDoc,
        batch_size: typing.Union[int, None] = None,
    ) -> typing.List[
        typing.Union[ImportResponseWithDoc[TDoc], ImportResponseFail[TDoc]]
    ]: ...

    @typing.overload
    def import_(
        self,
        documents: typing.List[TDoc],
        import_parameters: _ImportParameters,
        batch_size: typing.Union[int, None] = None,
    ) -> typing.List[ImportResponse[TDoc]]: ...

    @typing.overload
    def import_(
        self,
        documents: typing.Union[bytes, str],
        import_parameters: _ImportParameters = None,
        batch_size: typing.Union[int, None] = None,
    ) -> str: ...

    def import_(
        self,
        documents: typing.Union[bytes, str, typing.List[TDoc]],
        import_parameters: _ImportParameters = None,
        batch_size: typing.Union[int, None] = None,
    ) -> typing.Union[ImportResponse[TDoc], str]:
        """
        Import documents into the collection.

        This method supports various input types and import parameters.
        It can handle both individual documents and batches of documents.

        Args:
            documents: The documents to import.
            import_parameters: Parameters for the import operation.
            batch_size: The size of each batch for batch imports.

        Returns:
            The import response, which can be a list of responses or a string.

        Raises:
            TypesenseClientError: If an empty list of documents is provided.
        """
        if isinstance(documents, (str, bytes)):
            return self._import_raw(documents, import_parameters)

        if batch_size:
            return self._batch_import(documents, import_parameters, batch_size)

        return self._bulk_import(documents, import_parameters)

    def export(
        self,
        export_parameters: typing.Union[DocumentExportParameters, None] = None,
    ) -> str:
        """
        Export documents from the collection.

        Args:
            export_parameters (Union[DocumentExportParameters, None], optional):
                Parameters for the export operation.

        Returns:
            str: The exported documents as a string.
        """
        api_response: str = self.api_call.get(
            self._endpoint_path("export"),
            params=export_parameters,
            as_json=False,
            entity_type=str,
        )
        return api_response

    def search(self, search_parameters: SearchParameters) -> SearchResponse[TDoc]:
        """
        Search for documents in the collection.

        Args:
            search_parameters (SearchParameters): The search parameters.

        Returns:
            SearchResponse[TDoc]: The search response containing matching documents.
        """
        stringified_search_params = stringify_search_params(search_parameters)
        response: SearchResponse[TDoc] = self.api_call.get(
            self._endpoint_path("search"),
            params=stringified_search_params,
            entity_type=SearchResponse,
            as_json=True,
        )
        return response

    def delete(
        self,
        delete_parameters: typing.Union[DeleteQueryParameters, None] = None,
    ) -> DeleteResponse:
        """
        Delete documents from the collection based on given parameters.

        Args:
            delete_parameters (Union[DeleteQueryParameters, None], optional):
                Parameters for deletion.

        Returns:
            DeleteResponse: The response containing information about the deletion.
        """
        response: DeleteResponse = self.api_call.delete(
            self._endpoint_path(),
            params=delete_parameters,
            entity_type=DeleteResponse,
        )
        return response

    def _endpoint_path(self, action: typing.Union[str, None] = None) -> str:
        """
        Construct the API endpoint path for document operations.

        Args:
            action (Union[str, None], optional): The action to perform. Defaults to None.

        Returns:
            str: The constructed endpoint path.
        """
        from typesense.collections import Collections

        action = action or ""
        return "/".join(
            [
                Collections.resource_path,
                self.collection_name,
                self.resource_path,
                action,
            ],
        )

    def _import_raw(
        self,
        documents: typing.Union[bytes, str],
        import_parameters: _ImportParameters,
    ) -> str:
        """Import raw document data."""
        response: str = self.api_call.post(
            self._endpoint_path("import"),
            body=documents,
            params=import_parameters,
            as_json=False,
            entity_type=str,
        )

        return response

    def _batch_import(
        self,
        documents: typing.List[TDoc],
        import_parameters: _ImportParameters,
        batch_size: int,
    ) -> ImportResponse[TDoc]:
        """Import documents in batches."""
        response_objs: ImportResponse[TDoc] = []
        for batch_index in range(0, len(documents), batch_size):
            batch = documents[batch_index : batch_index + batch_size]
            api_response = self._bulk_import(batch, import_parameters)
            response_objs.extend(api_response)
        return response_objs

    def _bulk_import(
        self,
        documents: typing.List[TDoc],
        import_parameters: _ImportParameters,
    ) -> ImportResponse[TDoc]:
        """Import a list of documents in bulk."""
        document_strs = [json.dumps(doc) for doc in documents]
        if not document_strs:
            raise TypesenseClientError("Cannot import an empty list of documents.")

        docs_import = "\n".join(document_strs)
        res = self.api_call.post(
            self._endpoint_path("import"),
            body=docs_import,
            params=import_parameters,
            entity_type=str,
            as_json=False,
        )
        return self._parse_import_response(res)

    def _parse_import_response(self, response: str) -> ImportResponse[TDoc]:
        """Parse the import response string into a list of response objects."""
        response_objs: typing.List[ImportResponse] = []
        for res_obj_str in response.split("\n"):
            try:
                res_obj_json = json.loads(res_obj_str)
            except json.JSONDecodeError as decode_error:
                raise TypesenseClientError(
                    f"Invalid response - {res_obj_str}",
                ) from decode_error
            response_objs.append(res_obj_json)
        return response_objs
