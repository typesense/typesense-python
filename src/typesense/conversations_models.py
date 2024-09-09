"""
This module provides functionality for managing conversation models in Typesense.

Classes:
    - ConversationsModels: Handles operations related to conversation models.

Methods:
    - __init__: Initializes the ConversationsModels object.
    - __getitem__: Retrieves or creates a ConversationModel object for a given model_id.
    - create: Creates a new conversation model.
    - retrieve: Retrieves all conversation models.

Attributes:
    - resource_path: The API resource path for conversation models operations.

The ConversationsModels class interacts with the Typesense API to manage
conversation model operations.

It provides methods to create and retrieve conversation models, as well as access
individual ConversationModel objects.


For more information on conversation models and RAG, refer to the Conversational Search
[documentation](https://typesense.org/docs/27.0/api/conversational-search-rag.html)

This module uses type hinting and is compatible with Python 3.11+ as well as earlier
versions through the use of the typing_extensions library.
"""

import sys

from typesense.api_call import ApiCall
from typesense.types.conversations_model import (
    ConversationModelCreateSchema,
    ConversationModelSchema,
)

if sys.version_info > (3, 11):
    import typing
else:
    import typing_extensions as typing

from typesense.conversation_model import ConversationModel


class ConversationsModels(object):
    """
    Class for managing conversation models in Typesense.

    This class provides methods to interact with conversation models, including
    creating, retrieving, and accessing individual models.

    Attributes:
        resource_path (str): The API resource path for conversation models operations.
        api_call (ApiCall): The API call object for making requests.
        conversations_models (Dict[str, ConversationModel]):
            A dictionary of ConversationModel objects.
    """

    resource_path: typing.Final[str] = "/conversations/models"

    def __init__(self, api_call: ApiCall) -> None:
        """
        Initialize the ConversationsModels object.

        Args:
            api_call (ApiCall): The API call object for making requests.
        """
        self.api_call = api_call
        self.conversations_models: typing.Dict[str, ConversationModel] = {}

    def __getitem__(self, model_id: str) -> ConversationModel:
        """
        Get or create a ConversationModel object for a given model_id.

        Args:
            model_id (str): The ID of the conversation model.

        Returns:
            ConversationModel: The ConversationModel object for the given ID.
        """
        if model_id not in self.conversations_models:
            self.conversations_models[model_id] = ConversationModel(
                self.api_call,
                model_id,
            )
        return self.conversations_models[model_id]

    def create(self, model: ConversationModelCreateSchema) -> ConversationModelSchema:
        """
        Create a new conversation model.

        Args:
            model (ConversationModelCreateSchema):
                The schema for creating the conversation model.

        Returns:
            ConversationModelSchema: The created conversation model.
        """
        response = self.api_call.post(
            endpoint=ConversationsModels.resource_path,
            entity_type=ConversationModelSchema,
            as_json=True,
            body=model,
        )
        return response

    def retrieve(self) -> typing.List[ConversationModelSchema]:
        """
        Retrieve all conversation models.

        Returns:
            List[ConversationModelSchema]: A list of all conversation models.
        """
        response: typing.List[ConversationModelSchema] = self.api_call.get(
            endpoint=ConversationsModels.resource_path,
            entity_type=typing.List[ConversationModelSchema],
            as_json=True,
        )
        return response
