"""
Module for interacting with the stemming dictionaries endpoint of the Typesense API.

This module provides a class for managing stemming dictionaries in Typesense, including creating
and updating them.

Classes:
    - StemmingDictionaries: Handles operations related to stemming dictionaries.

Methods:
    - __init__: Initializes the StemmingDictionaries object.
    - __getitem__: Retrieves or creates a StemmingDictionary object for a given dictionary_id.
    - upsert: Creates or updates a stemming dictionary.
    - _upsert_list: Creates or updates a list of stemming dictionaries.
    - _dump_to_jsonl: Dumps a list of StemmingDictionaryCreateSchema objects to a JSONL string.
    - _parse_response: Parses the response from the upsert operation.
    - _upsert_raw: Performs the raw upsert operation.
    - _endpoint_path: Constructs the API endpoint path for this specific stemming dictionary.

The StemmingDictionaries class interacts with the Typesense API to manage stemming dictionary
operations.
It provides methods to create, update, and retrieve stemming dictionaries, as well as
access individual StemmingDictionary objects.

For more information on stemming dictionaries,
refer to the Stemming [documentation](https://typesense.org/docs/28.0/api/stemming.html)
"""

import sys

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

import json

from typesense.api_call import ApiCall
from typesense.stemming_dictionary import StemmingDictionary
from typesense.types.stemming import (
    StemmingDictionariesRetrieveSchema,
    StemmingDictionaryCreateSchema,
)


class StemmingDictionaries:
    """
    Class for managing stemming dictionaries in Typesense.

    This class provides methods to interact with stemming dictionaries, including
    creating, updating, and retrieving them.

    Attributes:
        api_call (ApiCall): The API call object for making requests.
        stemming_dictionaries (Dict[str, StemmingDictionary]): A dictionary of
            StemmingDictionary objects.
    """

    resource_path: typing.Final[str] = "/stemming/dictionaries"

    def __init__(self, api_call: ApiCall):
        """
        Initialize the StemmingDictionaries object.

        Args:
            api_call (ApiCall): The API call object for making requests.
        """
        self.api_call = api_call
        self.stemming_dictionaries: typing.Dict[str, StemmingDictionary] = {}

    def __getitem__(self, dictionary_id: str) -> StemmingDictionary:
        """
        Get or create an StemmingDictionary object for a given rule_id.

        Args:
            rule_id (str): The ID of the analytics rule.

        Returns:
            StemmingDictionary: The StemmingDictionary object for the given ID.
        """
        if not self.stemming_dictionaries.get(dictionary_id):
            self.stemming_dictionaries[dictionary_id] = StemmingDictionary(
                self.api_call,
                dictionary_id,
            )
        return self.stemming_dictionaries[dictionary_id]

    def retrieve(self) -> StemmingDictionariesRetrieveSchema:
        """
        Retrieve the list of stemming dictionaries.

        Returns:
            StemmingDictionariesRetrieveSchema: The list of stemming dictionaries.
        """
        response: StemmingDictionariesRetrieveSchema = self.api_call.get(
            self._endpoint_path(),
            entity_type=StemmingDictionariesRetrieveSchema,
        )
        return response

    @typing.overload
    def upsert(
        self,
        dictionary_id: str,
        word_root_combinations: typing.Union[str, bytes],
    ) -> str: ...

    @typing.overload
    def upsert(
        self,
        dictionary_id: str,
        word_root_combinations: typing.List[StemmingDictionaryCreateSchema],
    ) -> typing.List[StemmingDictionaryCreateSchema]: ...

    def upsert(
        self,
        dictionary_id: str,
        word_root_combinations: typing.Union[
            typing.List[StemmingDictionaryCreateSchema],
            str,
            bytes,
        ],
    ) -> typing.Union[str, typing.List[StemmingDictionaryCreateSchema]]:
        if isinstance(word_root_combinations, (str, bytes)):
            return self._upsert_raw(dictionary_id, word_root_combinations)

        return self._upsert_list(dictionary_id, word_root_combinations)

    def _upsert_list(
        self,
        dictionary_id: str,
        word_root_combinations: typing.List[StemmingDictionaryCreateSchema],
    ) -> typing.List[StemmingDictionaryCreateSchema]:
        word_combos_in_jsonl = self._dump_to_jsonl(word_root_combinations)
        response = self._upsert_raw(dictionary_id, word_combos_in_jsonl)
        return self._parse_response(response)

    def _dump_to_jsonl(
        self,
        word_root_combinations: typing.List[StemmingDictionaryCreateSchema],
    ) -> str:
        word_root_strs = [json.dumps(combo) for combo in word_root_combinations]

        return "\n".join(word_root_strs)

    def _parse_response(
        self,
        response: str,
    ) -> typing.List[StemmingDictionaryCreateSchema]:
        object_list: typing.List[StemmingDictionaryCreateSchema] = []

        for line in response.split("\n"):
            try:
                decoded = json.loads(line)
            except json.JSONDecodeError:
                raise ValueError(f"Failed to parse JSON from response: {line}")
            object_list.append(decoded)
        return object_list

    def _upsert_raw(
        self,
        dictionary_id: str,
        word_root_combinations: typing.Union[bytes, str],
    ) -> str:
        response: str = self.api_call.post(
            self._endpoint_path("import"),
            body=word_root_combinations,
            as_json=False,
            entity_type=str,
            params={"id": dictionary_id},
        )
        return response

    def _endpoint_path(self, action: typing.Union[str, None] = None) -> str:
        """
        Construct the API endpoint path for this specific stemming dictionary.

        Args:
            action (str, optional): The action to perform on the stemming dictionary.
                Defaults to None.

        Returns:
            str: The constructed endpoint path.
        """
        if action:
            return f"{StemmingDictionaries.resource_path}/{action}"
        return StemmingDictionaries.resource_path
