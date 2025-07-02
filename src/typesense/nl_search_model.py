"""
This module provides functionality for managing individual NL search models in Typesense.

Classes:
    - NLSearchModel: Handles operations related to a specific NL search model.

Methods:
    - __init__: Initializes the NLSearchModel object.
    - _endpoint_path: Constructs the API endpoint path for this specific NL search model.
    - retrieve: Retrieves the details of this specific NL search model.
    - update: Updates this specific NL search model.
    - delete: Deletes this specific NL search model.

The NLSearchModel class interacts with the Typesense API to manage operations on a
specific NL search model. It provides methods to retrieve, update,
and delete individual models.

This module uses type hinting and is compatible with Python 3.11+ as well as earlier
versions through the use of the typing_extensions library.
"""

from typesense.api_call import ApiCall
from typesense.types.nl_search_model import (
    NLSearchModelDeleteSchema,
    NLSearchModelSchema,
    NLSearchModelUpdateSchema,
)


class NLSearchModel:
    """
    Class for managing individual NL search models in Typesense.

    This class provides methods to interact with a specific NL search model,
    including retrieving, updating, and deleting it.

    Attributes:
        model_id (str): The ID of the NL search model.
        api_call (ApiCall): The API call object for making requests.
    """

    def __init__(self, api_call: ApiCall, model_id: str) -> None:
        """
        Initialize the NLSearchModel object.

        Args:
            api_call (ApiCall): The API call object for making requests.
            model_id (str): The ID of the NL search model.
        """
        self.model_id = model_id
        self.api_call = api_call

    def retrieve(self) -> NLSearchModelSchema:
        """
        Retrieve this specific NL search model.

        Returns:
            NLSearchModelSchema: The schema containing the NL search model details.
        """
        response = self.api_call.get(
            self._endpoint_path,
            as_json=True,
            entity_type=NLSearchModelSchema,
        )
        return response

    def update(self, model: NLSearchModelUpdateSchema) -> NLSearchModelSchema:
        """
        Update this specific NL search model.

        Args:
            model (NLSearchModelUpdateSchema):
              The schema containing the updated model details.

        Returns:
            NLSearchModelSchema: The schema containing the updated NL search model.
        """
        response: NLSearchModelSchema = self.api_call.put(
            self._endpoint_path,
            body=model,
            entity_type=NLSearchModelSchema,
        )
        return response

    def delete(self) -> NLSearchModelDeleteSchema:
        """
        Delete this specific NL search model.

        Returns:
            NLSearchModelDeleteSchema: The schema containing the deletion response.
        """
        response: NLSearchModelDeleteSchema = self.api_call.delete(
            self._endpoint_path,
            entity_type=NLSearchModelDeleteSchema,
        )
        return response

    @property
    def _endpoint_path(self) -> str:
        """
        Construct the API endpoint path for this specific NL search model.

        Returns:
            str: The constructed endpoint path.
        """
        from typesense.nl_search_models import NLSearchModels

        return "/".join([NLSearchModels.resource_path, self.model_id])
