"""
This module provides functionality for managing stopwords in Typesense.

Classes:
    - Stopwords: Handles operations related to stopwords and stopword sets.

Methods:
    - __init__: Initializes the Stopwords object.
    - __getitem__: Retrieves or creates a StopwordsSet object for a given stopwords_set_id.
    - upsert: Creates or updates a stopwords set.
    - retrieve: Retrieves all stopwords sets.

Attributes:
    - RESOURCE_PATH: The API resource path for stopwords operations.

The Stopwords class interacts with the Typesense API to manage stopwords operations.
It provides methods to create, update, and retrieve stopwords sets, as well as access
individual StopwordsSet objects.

This module uses type hinting and is compatible with Python 3.11+ as well as earlier
versions through the use of the typing_extensions library.
"""

import sys

from typesense.api_call import ApiCall
from typesense.stopwords_set import StopwordsSet
from typesense.types.stopword import (
    StopwordCreateSchema,
    StopwordSchema,
    StopwordsRetrieveSchema,
)

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing


class Stopwords:
    """
    Class for managing stopwords in Typesense.

    This class provides methods to interact with stopwords and stopwords sets, including
    creating, updating, retrieving, and accessing individual stopwords sets.

    Attributes:
        RESOURCE_PATH (str): The API resource path for stopwords operations.
        api_call (ApiCall): The API call object for making requests.
        stopwords_sets (Dict[str, StopwordsSet]): A dictionary of StopwordsSet objects.
    """

    resource_path: typing.Final[str] = "/stopwords"

    def __init__(self, api_call: ApiCall):
        """
        Initialize the Stopwords object.

        Args:
            api_call (ApiCall): The API call object for making requests.
        """
        self.api_call = api_call
        self.stopwords_sets: typing.Dict[str, StopwordsSet] = {}

    def __getitem__(self, stopwords_set_id: str) -> StopwordsSet:
        """
        Get or create a StopwordsSet object for a given stopwords_set_id.

        Args:
            stopwords_set_id (str): The ID of the stopwords set.

        Returns:
            StopwordsSet: The StopwordsSet object for the given ID.
        """
        if not self.stopwords_sets.get(stopwords_set_id):
            self.stopwords_sets[stopwords_set_id] = StopwordsSet(
                self.api_call,
                stopwords_set_id,
            )
        return self.stopwords_sets[stopwords_set_id]

    def upsert(
        self,
        stopwords_set_id: str,
        stopwords_set: StopwordCreateSchema,
    ) -> StopwordSchema:
        """
        Create or update a stopwords set.

        Args:
            stopwords_set_id (str): The ID of the stopwords set to upsert.
            stopwords_set (StopwordCreateSchema):
                The schema for creating or updating the stopwords set.

        Returns:
            StopwordSchema: The created or updated stopwords set.
        """
        response: StopwordSchema = self.api_call.put(
            "/".join([Stopwords.resource_path, stopwords_set_id]),
            body=stopwords_set,
            entity_type=StopwordSchema,
        )
        return response

    def retrieve(self) -> StopwordsRetrieveSchema:
        """
        Retrieve all stopwords sets.

        Returns:
            StopwordsRetrieveSchema: The schema containing all stopwords sets.
        """
        response: StopwordsRetrieveSchema = self.api_call.get(
            Stopwords.resource_path,
            as_json=True,
            entity_type=StopwordsRetrieveSchema,
        )
        return response
