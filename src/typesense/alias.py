"""
This module provides functionality for managing individual aliases in Typesense.

Classes:
    - Alias: Handles operations related to a specific alias.

Methods:
    - __init__: Initializes the Alias object.
    - retrieve: Retrieves the details of this specific alias.
    - delete: Deletes this specific alias.
    - _endpoint_path: Constructs the API endpoint path for this specific alias.

The Alias class interacts with the Typesense API to manage operations on a
specific alias. It provides methods to retrieve and delete individual aliases.

For more information on collection aliases, refer to the Collection Alias
[documentation](https://typesense.org/docs/27.0/api/collection-alias.html#create-or-update-an-alias)

This module uses type hinting and is compatible with Python 3.11+ as well as earlier
versions through the use of the typing_extensions library.
"""

from typesense.api_call import ApiCall
from typesense.types.alias import AliasSchema


class Alias(object):
    """
    Class for managing individual aliases in Typesense.

    This class provides methods to interact with a specific alias,
    including retrieving and deleting it.

    Attributes:
        api_call (ApiCall): The API call object for making requests.
        name (str): The name of the alias.
    """

    def __init__(self, api_call: ApiCall, name: str):
        """
        Initialize the Alias object.

        Args:
            api_call (ApiCall): The API call object for making requests.
            name (str): The name of the alias.
        """
        self.api_call = api_call
        self.name = name

    def retrieve(self) -> AliasSchema:
        """
        Retrieve this specific alias.

        Returns:
            AliasSchema: The schema containing the alias details.
        """
        response: AliasSchema = self.api_call.get(
            self._endpoint_path,
            entity_type=AliasSchema,
            as_json=True,
        )
        return response

    def delete(self) -> AliasSchema:
        """
        Delete this specific alias.

        Returns:
            AliasSchema: The schema containing the deletion response.
        """
        response = self.api_call.delete(self._endpoint_path, entity_type=AliasSchema)
        return response

    @property
    def _endpoint_path(self) -> str:
        """
        Construct the API endpoint path for this specific alias.

        Returns:
            str: The constructed endpoint path.
        """
        from typesense.aliases import Aliases

        return "/".join([Aliases.resource_path, self.name])
