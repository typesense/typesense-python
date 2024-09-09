"""
This module provides functionality for managing aliases in Typesense.

Classes:
    - Aliases: Handles operations related to aliases within a Typesense instance.

Methods:
    - __init__: Initializes the Aliases object.
    - __getitem__: Retrieves or creates an Alias object for a given alias name.
    - _endpoint_path: Constructs the API endpoint path for alias operations.
    - upsert: Creates or updates an alias.
    - retrieve: Retrieves all aliases.

Attributes:
    - RESOURCE_PATH: The API resource path for alias operations.

The Aliases class interacts with the Typesense API to manage alias operations.
It provides methods to create, update, and retrieve aliases, as well as access
individual Alias objects.

For more information on collection aliases, refer to the Collection Alias
[documentation](https://typesense.org/docs/27.0/api/collection-alias.html#create-or-update-an-alias)

This module uses type hinting and is compatible with Python 3.11+ as well as earlier
versions through the use of the typing_extensions library.
"""

import sys

from typesense.alias import Alias
from typesense.api_call import ApiCall
from typesense.types.alias import AliasCreateSchema, AliasesResponseSchema, AliasSchema

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing


class Aliases:
    """
    Class for managing aliases in Typesense.

    This class provides methods to interact with aliases, including
    creating, updating, and retrieving them.

    Attributes:
        RESOURCE_PATH (str): The API resource path for alias operations.
        api_call (ApiCall): The API call object for making requests.
        aliases (Dict[str, Alias]): A dictionary of Alias objects.
    """

    resource_path: typing.Final[str] = "/aliases"

    def __init__(self, api_call: ApiCall):
        """
        Initialize the Aliases object.

        Args:
            api_call (ApiCall): The API call object for making requests.
        """
        self.api_call = api_call
        self.aliases: typing.Dict[str, Alias] = {}

    def __getitem__(self, name: str) -> Alias:
        """
        Get or create an Alias object for a given alias name.

        Args:
            name (str): The name of the alias.

        Returns:
            Alias: The Alias object for the given name.
        """
        if not self.aliases.get(name):
            self.aliases[name] = Alias(self.api_call, name)
        return self.aliases.get(name)

    def upsert(self, name: str, mapping: AliasCreateSchema) -> AliasSchema:
        """
        Create or update an alias.

        Args:
            name (str): The name of the alias.
            mapping (AliasCreateSchema): The schema for creating or updating the alias.

        Returns:
            AliasSchema: The created or updated alias.
        """
        response: AliasSchema = self.api_call.put(
            self._endpoint_path(name),
            body=mapping,
            entity_type=AliasSchema,
        )
        return response

    def retrieve(self) -> AliasesResponseSchema:
        """
        Retrieve all aliases.

        Returns:
            AliasesResponseSchema: The schema containing all aliases.
        """
        response: AliasesResponseSchema = self.api_call.get(
            Aliases.resource_path,
            as_json=True,
            entity_type=AliasesResponseSchema,
        )
        return response

    def _endpoint_path(self, alias_name: str) -> str:
        """
        Construct the API endpoint path for alias operations.

        Args:
            alias_name (str): The name of the alias.

        Returns:
            str: The constructed endpoint path.
        """
        return "/".join([Aliases.resource_path, alias_name])
