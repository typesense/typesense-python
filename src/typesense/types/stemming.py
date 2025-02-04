"""Stemming types for Typesense Python Client."""

import sys

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing


class StemmingDictionaryCreateSchema(typing.TypedDict):
    """
    Schema for creating a [stemming dictionary](https://typesense.org/docs/28/api/stemming.html#creating-a-stemming-dictionary).

    Attributes:
        name (str): The name of the stemming dictionary.
        words (list[str]): The list of words in the stemming dictionary.
    """

    word: str
    root: str


class StemmingDictionarySchema(typing.TypedDict):
    """
    Schema for a stemming dictionary.

    Attributes:
        id (str): The ID of the stemming dictionary.
        words (list[StemmingDictionarySchema]): The list of words and their roots in the stemming dictionary.
    """

    id: str
    words: typing.List[StemmingDictionaryCreateSchema]


class StemmingDictionariesRetrieveSchema(typing.TypedDict):
    """
    Schema for retrieving stemming dictionaries.

    Attributes:
        data (list[str]): The list of stemming dictionary names.
    """

    dictionaries: typing.List[str]
