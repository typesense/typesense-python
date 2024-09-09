"""
This module provides functionality for managing individual conversation models in Typesense.

Classes:
    - ConversationModel: Handles operations related to a specific conversation model.

Methods:
    - __init__: Initializes the ConversationModel object.
    - _endpoint_path: Constructs the API endpoint path for this specific conversation model.
    - retrieve: Retrieves the details of this specific conversation model.
    - update: Updates this specific conversation model.
    - delete: Deletes this specific conversation model.

The ConversationModel class interacts with the Typesense API to manage operations on a
specific conversation model. It provides methods to retrieve, update,
and delete individual models.

For more information on conversation models and RAG, refer to the Conversational Search
[documentation](https://typesense.org/docs/27.0/api/conversational-search-rag.html)

This module uses type hinting and is compatible with Python 3.11+ as well as earlier
versions through the use of the typing_extensions library.
"""

from typesense.api_call import ApiCall
from typesense.types.conversations_model import (
    ConversationModelCreateSchema,
    ConversationModelDeleteSchema,
    ConversationModelSchema,
)


class ConversationModel:
    """
    Class for managing individual conversation models in Typesense.

    This class provides methods to interact with a specific conversation model,
    including retrieving, updating, and deleting it.

    Attributes:
        model_id (str): The ID of the conversation model.
        api_call (ApiCall): The API call object for making requests.
    """

    def __init__(self, api_call: ApiCall, model_id: str) -> None:
        """
        Initialize the ConversationModel object.

        Args:
            api_call (ApiCall): The API call object for making requests.
            model_id (str): The ID of the conversation model.
        """
        self.model_id = model_id
        self.api_call = api_call

    def retrieve(self) -> ConversationModelSchema:
        """
        Retrieve this specific conversation model.

        Returns:
            ConversationModelSchema: The schema containing the conversation model details.
        """
        response = self.api_call.get(
            self._endpoint_path,
            as_json=True,
            entity_type=ConversationModelSchema,
        )
        return response

    def update(self, model: ConversationModelCreateSchema) -> ConversationModelSchema:
        """
        Update this specific conversation model.

        Args:
            model (ConversationModelCreateSchema):
              The schema containing the updated model details.

        Returns:
            ConversationModelSchema: The schema containing the updated conversation model.
        """
        response: ConversationModelSchema = self.api_call.put(
            self._endpoint_path,
            body=model,
            entity_type=ConversationModelSchema,
        )
        return response

    def delete(self) -> ConversationModelDeleteSchema:
        """
        Delete this specific conversation model.

        Returns:
            ConversationModelDeleteSchema: The schema containing the deletion response.
        """
        response: ConversationModelDeleteSchema = self.api_call.delete(
            self._endpoint_path,
            entity_type=ConversationModelDeleteSchema,
        )
        return response

    @property
    def _endpoint_path(self) -> str:
        """
        Construct the API endpoint path for this specific conversation model.

        Returns:
            str: The constructed endpoint path.
        """
        from typesense.conversations_models import ConversationsModels

        return "/".join([ConversationsModels.resource_path, self.model_id])
