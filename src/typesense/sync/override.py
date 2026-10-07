"""
This module provides async functionality for managing individual overrides in Typesense.

Classes:
    - Override: Handles async operations related to a specific override within a collection.

Methods:
    - __init__: Initializes the Override object.
    - retrieve: Retrieves the details of this specific override.
    - delete: Deletes this specific override.

Attributes:
    - _endpoint_path: The API endpoint path for this specific override.

The Override class interacts with the Typesense API to manage operations on a
specific override within a collection. It provides methods to retrieve and delete
individual overrides.

For more information regarding Overrides, refer to the Curation [documentation]
(https://typesense.org/docs/27.0/api/curation.html#curation).

This module uses type hinting and is compatible with Python 3.11+ as well as earlier
versions through the use of the typing_extensions library.
"""

from .api_call import ApiCall
from typesense.logger import warn_deprecation
from typesense.types.override import OverrideDeleteSchema, OverrideSchema


class Override:
    """
    Class for managing individual overrides in a Typesense collection (async).

    This class provides methods to interact with a specific override,
    including retrieving and deleting it.

    Attributes:
        api_call (ApiCall): The API call object for making requests.
        collection_name (str): The name of the collection.
        override_id (str): The ID of the override.
    """

    def __init__(
        self,
        api_call: ApiCall,
        collection_name: str,
        override_id: str,
    ) -> None:
        """
        Initialize the Override object.

        Args:
            api_call (ApiCall): The API call object for making requests.
            collection_name (str): The name of the collection.
            override_id (str): The ID of the override.
        """
        self.api_call = api_call
        self.collection_name = collection_name
        self.override_id = override_id

    def retrieve(self) -> OverrideSchema:
        """
        Retrieve this specific override.

        Returns:
            OverrideSchema: The schema containing the override details.
        """
        response: OverrideSchema = self.api_call.get(
            self._endpoint_path,
            entity_type=OverrideSchema,
            as_json=True,
        )
        return response

    def delete(self) -> OverrideDeleteSchema:
        """
        Delete this specific override.

        Returns:
            OverrideDeleteSchema: The schema containing the deletion response.
        """
        response: OverrideDeleteSchema = self.api_call.delete(
            self._endpoint_path,
            entity_type=OverrideDeleteSchema,
        )
        return response

    @property
    @warn_deprecation(
        "The override API (collections/{collection}/overrides/{override_id}) is deprecated is removed on v30+. "
        "Use curation sets (curation_sets) instead.",
        flag_name="overrides_deprecation",
    )
    def _endpoint_path(self) -> str:
        """
        Construct the API endpoint path for this specific override.

        Returns:
            str: The constructed endpoint path.
        """
        from .collections import Collections
        from .overrides import Overrides

        return "/".join(
            [
                Collections.resource_path,
                self.collection_name,
                Overrides.resource_path,
                self.override_id,
            ],
        )
