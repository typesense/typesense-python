"""Stopword types for Typesense Python Client."""

import sys

from typesense.types.collection import Locales

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing


class StopwordCreateSchema(typing.TypedDict):
    """
    Schema for creating a new stopword.

    Attributes:
        stopwords (list[str]): The stopwords to be added.
    """

    stopwords: typing.List[str]
    locale: typing.NotRequired[Locales]


class StopwordSchema(StopwordCreateSchema):
    """
    Schema for a stopword.

    Attributes:
        stopwords (list[str]): The stopwords to be added.
    """

    id: str


class StopwordsSingleRetrieveSchema(typing.TypedDict):
    """
    Response schema for retrieving a single stopword.

    Attributes:
        stopwords (StopwordSchema): The Stopword.
    """

    stopwords: StopwordSchema


class StopwordsRetrieveSchema(typing.TypedDict):
    """
    Response schema for retrieving stopwords.

    Attributes:
        stopwords (list[str]): The list of stopwords.
    """

    stopwords: typing.List[StopwordSchema]


class StopwordDeleteSchema(typing.TypedDict):
    """
    Response schema for deleting a stopword.

    Attributes:
        id (str): The ID of the stopword.
    """

    id: str
