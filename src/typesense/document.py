"""
This module provides functionality for managing individual documents in Typesense collections.

Classes:
    - Document: Handles operations related to a specific document within a collection.

Methods:
    - __init__: Initializes the Document object.
    - _endpoint_path: Constructs the API endpoint path for this specific document.
    - retrieve: Retrieves the details of this specific document.
    - update: Updates this specific document.
    - delete: Deletes this specific document.

The Document class interacts with the Typesense API to manage operations on a
specific document within a collection. It provides methods to retrieve, update,
and delete individual documents.

This module uses type hinting and is compatible with Python 3.11+ as well as earlier
versions through the use of the typing_extensions library.
"""

import sys

from typesense.api_call import ApiCall
from typesense.types.document import (
    DeleteSingleDocumentParameters,
    DirtyValuesParameters,
    DocumentSchema,
    RetrieveParameters,
)

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

TDoc = typing.TypeVar("TDoc", bound=DocumentSchema)


class Document(typing.Generic[TDoc]):
    """
    Class for managing individual documents in a Typesense collection.

    This class provides methods to interact with a specific document,
    including retrieving, updating, and deleting it.

    Attributes:
        api_call (ApiCall): The API call object for making requests.
        collection_name (str): The name of the collection.
        document_id (str): The ID of the document.
    """

    def __init__(
        self,
        api_call: ApiCall,
        collection_name: str,
        document_id: str,
    ) -> None:
        """
        Initialize the Document object.

        Args:
            api_call (ApiCall): The API call object for making requests.
            collection_name (str): The name of the collection.
            document_id (str): The ID of the document.
        """
        self.api_call = api_call
        self.collection_name = collection_name
        self.document_id = document_id

    def retrieve(
        self,
        retrieve_parameters: typing.Union[RetrieveParameters, None] = None,
    ) -> TDoc:
        """
        Retrieve this specific document.

        Returns:
            TDoc: The retrieved document.
        """
        response: TDoc = self.api_call.get(
            endpoint=self._endpoint_path,
            entity_type=typing.Dict[str, str],
            as_json=True,
            params=retrieve_parameters,
        )
        return response

    def update(
        self,
        document: TDoc,
        dirty_values_parameters: typing.Union[DirtyValuesParameters, None] = None,
    ) -> TDoc:
        """
        Update this specific document.

        Args:
            document (TDoc): The updated document data.
            dirty_values_parameters (Union[DirtyValuesParameters, None], optional):
                Parameters for handling dirty values.

        Returns:
            TDoc: The updated document.
        """
        response = self.api_call.patch(
            self._endpoint_path,
            body=document,
            params=dirty_values_parameters,
            entity_type=typing.Dict[str, str],
        )
        return typing.cast(TDoc, response)

    def delete(
        self,
        delete_parameters: typing.Union[DeleteSingleDocumentParameters, None] = None,
    ) -> TDoc:
        """
        Delete this specific document.

        Returns:
            TDoc: The deleted document.
        """
        response: TDoc = self.api_call.delete(
            self._endpoint_path,
            entity_type=typing.Dict[str, str],
            params=delete_parameters,
        )
        return response

    @property
    def _endpoint_path(self) -> str:
        """
        Construct the API endpoint path for this specific document.

        Returns:
            str: The constructed endpoint path.
        """
        from typesense.collections import Collections
        from typesense.documents import Documents

        return "/".join(
            [
                Collections.resource_path,
                self.collection_name,
                Documents.resource_path,
                self.document_id,
            ],
        )
