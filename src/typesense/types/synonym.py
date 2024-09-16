"""Synonym types for Typesense Python Client."""

import sys

from typesense.types.collection import Locales

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing


class SynonymCreateSchema(typing.TypedDict):
    """
    The schema for the request of the Synonyms.upsert method.

    Attributes:
        synonyms (list[str]): The synonyms list.

        root (str): The root string.

        locale (Locales): The locale.

        symbols_to_index (list[str]): The symbols to index.
    """

    synonyms: typing.List[str]
    root: typing.NotRequired[str]
    locale: typing.NotRequired[Locales]
    symbols_to_index: typing.NotRequired[typing.List[str]]


class SynonymSchema(SynonymCreateSchema):
    """
    The schema for the response of the Synonyms.upsert method.

    Attributes:
        id (str): The ID of the synonym.

        synonyms (list[str]): The synonyms list.

        root (str): The root string.

        locale (Locales): The locale.

        symbols_to_index (list[str]): The symbols to index.
    """

    id: str


class SynonymsRetrieveSchema(typing.TypedDict):
    """
    The schema for the response of the Synonyms.retrieve method.

    Attributes:
        synonyms(list[SynonymSchema]): The list of synonyms.
    """

    synonyms: typing.List[SynonymSchema]


class SynonymDeleteSchema(typing.TypedDict):
    """
    The schema for the response of the Synonyms.delete method.

    Attributes:
        id (str): The ID of the synonym.
    """

    id: str
