"""
This module provides functionality for managing individual stopwords sets in Typesense.

Classes:
    - StopwordsSet: Handles operations related to a specific stopwords set.

Methods:
    - __init__: Initializes the StopwordsSet object.
    - retrieve: Retrieves the details of this specific stopwords set.
    - delete: Deletes this specific stopwords set.
    - _endpoint_path: Constructs the API endpoint path for this specific stopwords set.

The StopwordsSet class interacts with the Typesense API to manage operations on a
specific stopwords set. It provides methods to retrieve and delete individual stopwords sets.

For more information regarding Stopwords, refer to the Stopwords [documentation]
(https://typesense.org/docs/27.0/api/stopwords.html).

This module uses type hinting and is compatible with Python 3.11+ as well as earlier
versions through the use of the typing_extensions library.
"""

from typesense.api_call import ApiCall
from typesense.types.stopword import StopwordDeleteSchema, StopwordsSingleRetrieveSchema


class StopwordsSet:
    """
    Class for managing individual stopwords sets in Typesense.

    This class provides methods to interact with a specific stopwords set,
    including retrieving and deleting it.

    Attributes:
        stopwords_set_id (str): The ID of the stopwords set.
        api_call (ApiCall): The API call object for making requests.
    """

    def __init__(self, api_call: ApiCall, stopwords_set_id: str) -> None:
        """
        Initialize the StopwordsSet object.

        Args:
            api_call (ApiCall): The API call object for making requests.
            stopwords_set_id (str): The ID of the stopwords set.
        """
        self.stopwords_set_id = stopwords_set_id
        self.api_call = api_call

    def retrieve(self) -> StopwordsSingleRetrieveSchema:
        """
        Retrieve this specific stopwords set.

        Returns:
            StopwordsSingleRetrieveSchema: The schema containing the stopwords set details.
        """
        response: StopwordsSingleRetrieveSchema = self.api_call.get(
            self._endpoint_path,
            as_json=True,
            entity_type=StopwordsSingleRetrieveSchema,
        )
        return response

    def delete(self) -> StopwordDeleteSchema:
        """
        Delete this specific stopwords set.

        Returns:
            StopwordDeleteSchema: The schema containing the deletion response.
        """
        response: StopwordDeleteSchema = self.api_call.delete(
            self._endpoint_path,
            entity_type=StopwordDeleteSchema,
        )
        return response

    @property
    def _endpoint_path(self) -> str:
        """
        Construct the API endpoint path for this specific stopwords set.

        Returns:
            str: The constructed endpoint path.
        """
        from typesense.stopwords import Stopwords

        return "/".join([Stopwords.resource_path, self.stopwords_set_id])
