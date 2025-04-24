"""
This module provides functionality for managing collections in the Typesense API.

It contains the Collections class, which allows for creating, retrieving, and
accessing individual collections.

Classes:
    Collections: Manages collections in the Typesense API.

Dependencies:
    - typesense.api_call: Provides the ApiCall class for making API requests.
    - typesense.collection: Provides the Collection class for individual collection operations.
    - typesense.types.collection: Provides CollectionCreateSchema and CollectionSchema types.
    - typesense.types.document: Provides DocumentSchema type.

Note: This module uses conditional imports to support both Python 3.11+ and earlier versions.
"""

import sys

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

from typesense.api_call import ApiCall
from typesense.collection import Collection
from typesense.types.collection import CollectionCreateSchema, CollectionSchema
from typesense.types.document import DocumentSchema

TDoc = typing.TypeVar("TDoc", bound=DocumentSchema)


class Collections(typing.Generic[TDoc]):
    """
    Manages collections in the Typesense API.

    This class provides methods to create, retrieve, and access individual collections.
    It is generic over the document type TDoc, which should be a subtype of DocumentSchema.

    Attributes:
        resource_path (str): The API endpoint path for collections operations.
        api_call (ApiCall): The ApiCall instance for making API requests.
        collections (Dict[str, Collection[TDoc]]):
           A dictionary of Collection instances, keyed by collection name.
    """

    resource_path: typing.Final[str] = "/collections"

    def __init__(self, api_call: ApiCall):
        """
        Initialize the Collections instance.

        Args:
            api_call (ApiCall): The ApiCall instance for making API requests.
        """
        self.api_call = api_call
        self.collections: typing.Dict[str, Collection[TDoc]] = {}

    def __contains__(self, collection_name: str) -> bool:
        """
        Check if a collection exists in Typesense.

        This method tries to retrieve the specified collection to check for its existence,
        utilizing the Collection.retrieve() method but without caching non-existent collections.

        Args:
            collection_name (str): The name of the collection to check.

        Returns:
            bool: True if the collection exists, False otherwise.
        """
        if collection_name in self.collections:
            try:  # noqa: WPS229, WPS529

                self.collections[collection_name].retrieve()  # noqa: WPS529
                return True
            except Exception:
                self.collections.pop(collection_name, None)
                return False

        try:  # noqa: WPS229, WPS529
            Collection(self.api_call, collection_name).retrieve()
            return True
        except Exception:
            return False

    def __getitem__(self, collection_name: str) -> Collection[TDoc]:
        """
        Get or create a Collection instance for a given collection name.

        This method allows accessing collections using dictionary-like syntax.
        If the Collection instance doesn't exist, it creates a new one.

        Args:
            collection_name (str): The name of the collection to access.

        Returns:
            Collection[TDoc]: The Collection instance for the specified collection name.

        Example:
            >>> collections = Collections(api_call)
            >>> fruits_collection = collections['fruits']
        """
        if not self.collections.get(collection_name):
            self.collections[collection_name] = Collection(
                self.api_call,
                collection_name,
            )
        return self.collections[collection_name]

    def create(self, schema: CollectionCreateSchema) -> CollectionSchema:
        """
        Create a new collection in Typesense.

        Args:
            schema (CollectionCreateSchema):
               The schema defining the structure of the new collection.

        Returns:
            CollectionSchema:
                The schema of the created collection, as returned by the API.

        Example:
            >>> collections = Collections(api_call)
            >>> schema = {
            ...     "name": "companies",
            ...     "fields": [
            ...         {"name": "company_name", "type": "string" },
            ...         {"name": "num_employees", "type": "int32" },
            ...         {"name": "country", "type": "string", "facet": True }
            ...     ],
            ...     "default_sorting_field": "num_employees"
            ... }
            >>> created_schema = collections.create(schema)
        """
        call: CollectionSchema = self.api_call.post(
            endpoint=Collections.resource_path,
            entity_type=CollectionSchema,
            as_json=True,
            body=schema,
        )
        return call

    def retrieve(self) -> typing.List[CollectionSchema]:
        """
        Retrieve all collections from Typesense.

        Returns:
            List[CollectionSchema]:
               A list of schemas for all collections in the Typesense instance.

        Example:
            >>> collections = Collections(api_call)
            >>> all_collections = collections.retrieve()
            >>> for collection in all_collections:
            ...     print(collection['name'])
        """
        call: typing.List[CollectionSchema] = self.api_call.get(
            endpoint=Collections.resource_path,
            as_json=True,
            entity_type=typing.List[CollectionSchema],
        )
        return call
