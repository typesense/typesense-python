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

from .conversation_model import ConversationModel


class ConversationsModels(object):
    RESOURCE_PATH = "/conversations/models"

    def __init__(self, api_call: ApiCall) -> None:
        self.api_call = api_call
        self.conversations_models: typing.Dict[str, ConversationModel] = {}

    def __getitem__(self, model_id: str) -> ConversationModel:
        if model_id not in self.conversations_models:
            self.conversations_models[model_id] = ConversationModel(
                self.api_call,
                model_id,
            )

        return self.conversations_models[model_id]

    def create(self, model: ConversationModelCreateSchema) -> ConversationModelSchema:
        response = self.api_call.post(
            endpoint=ConversationsModels.RESOURCE_PATH,
            entity_type=ConversationModelSchema,
            as_json=True,
            body=model,
        )
        return response

    def retrieve(self) -> typing.List[ConversationModelSchema]:
        response: typing.List[ConversationModelSchema] = self.api_call.get(
            endpoint=ConversationsModels.RESOURCE_PATH,
            entity_type=typing.List[ConversationModelSchema],
            as_json=True,
        )
        return response
