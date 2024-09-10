"""
This module provides functionality for managing individual collections in the Typesense API.

It contains the Collection class, which allows for retrieving, updating, and deleting
collections, as well as managing documents, overrides, and synonyms within a collection.

Classes:
    Collection: Manages operations on a single collection in the Typesense API.

Dependencies:
    - typesense.api_call: Provides the ApiCall class for making API requests.
    - typesense.documents: Provides the Documents class for managing documents.
    - typesense.overrides: Provides the Overrides class for managing overrides.
    - typesense.synonyms: Provides the Synonyms class for managing synonyms.
    - typesense.types.collection: Provides CollectionSchema and CollectionUpdateSchema types.
    - typesense.types.document: Provides DocumentSchema type.

Note: This module uses conditional imports to support both Python 3.11+ and earlier versions.
"""

import sys

from typesense.types.collection import CollectionSchema, CollectionUpdateSchema

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

from typesense.api_call import ApiCall
from typesense.documents import Documents
from typesense.overrides import Overrides
from typesense.synonyms import Synonyms
from typesense.types.document import DocumentSchema

TDoc = typing.TypeVar("TDoc", bound=DocumentSchema)


class Collection(typing.Generic[TDoc]):
    """
    Manages operations on a single collection in the Typesense API.

    This class provides methods to retrieve, update, and delete a collection,
    as well as access to documents, overrides, and synonyms within the collection.
    It is generic over the document type TDoc, which should be a subtype of DocumentSchema.

    Attributes:
        name (str): The name of the collection.
        api_call (ApiCall): The ApiCall instance for making API requests.
        documents (Documents[TDoc]): Instance for managing documents in this collection.
        overrides (Overrides): Instance for managing overrides in this collection.
        synonyms (Synonyms): Instance for managing synonyms in this collection.
    """

    def __init__(self, api_call: ApiCall, name: str):
        """
        Initialize the Collection instance.

        Args:
            api_call (ApiCall): The ApiCall instance for making API requests.
            name (str): The name of the collection.
        """
        self.name = name
        self.api_call = api_call
        self.documents: Documents[TDoc] = Documents(api_call, name)
        self.overrides = Overrides(api_call, name)
        self.synonyms = Synonyms(api_call, name)

    def retrieve(self) -> CollectionSchema:
        """
        Retrieve the schema of this collection from Typesense.

        Returns:
            CollectionSchema: The schema of the collection.
        """
        response: CollectionSchema = self.api_call.get(
            endpoint=self._endpoint_path,
            entity_type=CollectionSchema,
            as_json=True,
        )
        return response

    def update(self, schema_change: CollectionUpdateSchema) -> CollectionUpdateSchema:
        """
        Update the schema of this collection in Typesense.

        Args:
            schema_change (CollectionUpdateSchema):
                The changes to apply to the collection schema.

        Returns:
            CollectionUpdateSchema: The updated schema of the collection.
        """
        response: CollectionUpdateSchema = self.api_call.patch(
            endpoint=self._endpoint_path,
            body=schema_change,
            entity_type=CollectionUpdateSchema,
        )
        return response

    def delete(
        self,
        delete_parameters: typing.Union[
            typing.Dict[str, typing.Union[str, bool]],
            None,
        ] = None,
    ) -> CollectionSchema:
        """
        Delete this collection from Typesense.

        Args:
            delete_parameters (Union[Dict[str, Union[str, bool]], None], optional):
                Additional parameters for the delete operation. Defaults to None.

        Returns:
            CollectionSchema: The schema of the deleted collection.
        """
        response: CollectionSchema = self.api_call.delete(
            self._endpoint_path,
            entity_type=CollectionSchema,
            params=delete_parameters,
        )
        return response

    @property
    def _endpoint_path(self) -> str:
        """
        Get the API endpoint path for this collection.

        Returns:
            str: The full endpoint path for the collection.
        """
        from typesense.collections import Collections

        return "/".join([Collections.resource_path, self.name])
