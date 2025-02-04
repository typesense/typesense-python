"""
Module for managing individual stemming dictionaries in Typesense.

This module provides a class for managing individual stemming dictionaries in Typesense,
including retrieving them.

Classes:
    - StemmingDictionary: Handles operations related to individual stemming dictionaries.

Methods:
    - __init__: Initializes the StemmingDictionary object.
    - retrieve: Retrieves this specific stemming dictionary.

The StemmingDictionary class interacts with the Typesense API to manage operations on a
specific stemming dictionary. It provides methods to retrieve the dictionary details.

For more information on stemming dictionaries, refer to the Stemming
[documentation](https://typesense.org/docs/28.0/api/stemming.html)

This module uses type hinting and is compatible with Python 3.11+ as well as earlier
versions through the use of the typing_extensions library.
"""

from typesense.api_call import ApiCall
from typesense.types.stemming import StemmingDictionarySchema


class StemmingDictionary:
    """
    Class for managing individual stemming dictionaries in Typesense.

    This class provides methods to interact with a specific stemming dictionary,
    including retrieving it.

    Attributes:
        api_call (ApiCall): The API call object for making requests.
        dict_id (str): The ID of the stemming dictionary.
    """

    def __init__(self, api_call: ApiCall, dict_id: str):
        """
        Initialize the StemmingDictionary object.

        Args:
            api_call (ApiCall): The API call object for making requests.
            dict_id (str): The ID of the stemming dictionary.
        """
        self.api_call = api_call
        self.dict_id = dict_id

    def retrieve(self) -> StemmingDictionarySchema:
        """
        Retrieve this specific stemming dictionary.

        Returns:
            StemmingDictionarySchema: The schema containing the stemming dictionary details.
        """
        response: StemmingDictionarySchema = self.api_call.get(
            self._endpoint_path,
            entity_type=StemmingDictionarySchema,
            as_json=True,
        )
        return response

    @property
    def _endpoint_path(self) -> str:
        """
        Construct the API endpoint path for this specific analytics rule.

        Returns:
            str: The constructed endpoint path.
        """
        from typesense.stemming_dictionaries import StemmingDictionaries

        return "/".join([StemmingDictionaries.resource_path, self.dict_id])
