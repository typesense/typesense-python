"""
This module provides functionality for managing individual synonyms in Typesense.

Classes:
    - Synonym: Handles operations related to a specific synonym within a collection.

Methods:
    - __init__: Initializes the Synonym object.
    - _endpoint_path: Constructs the API endpoint path for this specific synonym.
    - retrieve: Retrieves the details of this specific synonym.
    - delete: Deletes this specific synonym.

The Synonym class interacts with the Typesense API to manage operations on a
specific synonym within a collection. It provides methods to retrieve and delete
individual synonyms.

For more information regarding Synonyms, refer to the Synonyms [documentation]
(https://typesense.org/docs/27.0/api/synonyms.html#synonyms).

This module uses type hinting and is compatible with Python 3.11+ as well as earlier
versions through the use of the typing_extensions library.
"""

from typesense.api_call import ApiCall
from typesense.types.synonym import SynonymDeleteSchema, SynonymSchema


class Synonym:
    """
    Class for managing individual synonyms in a Typesense collection.

    This class provides methods to interact with a specific synonym,
    including retrieving and deleting it.

    Attributes:
        api_call (ApiCall): The API call object for making requests.
        collection_name (str): The name of the collection.
        synonym_id (str): The ID of the synonym.
    """

    def __init__(
        self,
        api_call: ApiCall,
        collection_name: str,
        synonym_id: str,
    ) -> None:
        """
        Initialize the Synonym object.

        Args:
            api_call (ApiCall): The API call object for making requests.
            collection_name (str): The name of the collection.
            synonym_id (str): The ID of the synonym.
        """
        self.api_call = api_call
        self.collection_name = collection_name
        self.synonym_id = synonym_id

    def retrieve(self) -> SynonymSchema:
        """
        Retrieve this specific synonym.

        Returns:
            SynonymSchema: The schema containing the synonym details.
        """
        return self.api_call.get(self._endpoint_path(), entity_type=SynonymSchema)

    def delete(self) -> SynonymDeleteSchema:
        """
        Delete this specific synonym.

        Returns:
            SynonymDeleteSchema: The schema containing the deletion response.
        """
        return self.api_call.delete(
            self._endpoint_path(),
            entity_type=SynonymDeleteSchema,
        )

    def _endpoint_path(self) -> str:
        """
        Construct the API endpoint path for this specific synonym.

        Returns:
            str: The constructed endpoint path.
        """
        from typesense.collections import Collections
        from typesense.synonyms import Synonyms

        return "/".join(
            [
                Collections.resource_path,
                self.collection_name,
                Synonyms.resource_path,
                self.synonym_id,
            ],
        )
