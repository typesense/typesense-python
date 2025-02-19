"""
Module for managing stemming dictionaries in Typesense.

This module provides a class for managing stemming dictionaries in Typesense,
including creating, updating, and retrieving them.

Classes:
    - Stemming: Handles operations related to stemming dictionaries.

Attributes:
    - StemmingDictionaries: The StemmingDictionaries object for managing stemming dictionaries.

Methods:
    - __init__: Initializes the Stemming object.

The Stemming class interacts with the Typesense API to manage stemming dictionary operations.
It provides access to the StemmingDictionaries object for managing stemming dictionaries.

For more information on stemming dictionaries, refer to the Stemming
[documentation](https://typesense.org/docs/28.0/api/stemming.html)

This module uses type hinting and is compatible with Python 3.11+ as well as earlier
versions through the use of the typing_extensions library.
"""

from typesense.api_call import ApiCall
from typesense.stemming_dictionaries import StemmingDictionaries


class Stemming(object):
    """
    Class for managing stemming dictionaries in Typesense.

    This class provides methods to interact with stemming dictionaries, including
    creating, updating, and retrieving them.

    Attributes:
        dictionaries (StemmingDictionaries): The StemmingDictionaries object for managing
            stemming dictionaries.
    """

    def __init__(self, api_call: ApiCall):
        """
        Initialize the Stemming object.

        Args:
            api_call (ApiCall): The API call object for making requests.
        """
        self.api_call = api_call
        self.dictionaries = StemmingDictionaries(api_call)
