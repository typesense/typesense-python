"""Alias types for Typesense Python Client."""

import sys

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing


class AliasCreateSchema(typing.TypedDict):
    """
    The schema for the request of the Aliases.create method.

    Attributes:
        collection_name (str): The name of the collection.
    """

    collection_name: str


class AliasSchema(AliasCreateSchema):
    """
    The schema for the response of the Aliases.create method.

    Attributes:
        name (str): The name of the alias.

        collection_name (str): The name of the collection.
    """

    name: str


class AliasesResponseSchema(typing.TypedDict):
    """
    The schema for the response of the Aliases.retrieve method.

    Attributes:
        aliases(list[CollectionAliasSchema]): The list of aliases.
    """

    aliases: typing.List[AliasSchema]
