"""Synonym Set types for Typesense Python Client."""

import sys

from typesense.types.collection import Locales

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing


class SynonymItemSchema(typing.TypedDict):
    """
    Schema representing an individual synonym item inside a synonym set.

    Attributes:
        id (str): Unique identifier for the synonym item.
        synonyms (list[str]): The synonyms array.
        root (str, optional): For 1-way synonyms, indicates the root word that words in
            the synonyms parameter map to.
        locale (Locales, optional): Locale for the synonym.
        symbols_to_index (list[str], optional): Symbols to index as-is in synonyms.
    """

    id: str
    synonyms: typing.List[str]
    root: typing.NotRequired[str]
    locale: typing.NotRequired[Locales]
    symbols_to_index: typing.NotRequired[typing.List[str]]

class SynonymItemDeleteSchema(typing.TypedDict):
    """
    Schema for deleting a synonym item.
    """

    id: str

class SynonymSetCreateSchema(typing.TypedDict):
    """
    Schema for creating or updating a synonym set.

    Attributes:
        items (list[SynonymItemSchema]): Array of synonym items.
    """

    items: typing.List[SynonymItemSchema]


class SynonymSetSchema(SynonymSetCreateSchema):
    """
    Schema representing a synonym set.

    Attributes:
        name (str): Name of the synonym set.
    """

    name: str


class SynonymSetsRetrieveSchema(typing.List[SynonymSetSchema]):
    """Deprecated alias for list of synonym sets; use List[SynonymSetSchema] directly."""


class SynonymSetRetrieveSchema(SynonymSetCreateSchema):
    """Response schema for retrieving a single synonym set by name."""


class SynonymSetDeleteSchema(typing.TypedDict):
    """Response schema for deleting a synonym set.

    Attributes:
        name (str): Name of the deleted synonym set.
    """

    name: str