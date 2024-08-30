from typesense.api_call import ApiCall
from typesense.types.conversations_model import (
    ConversationModelCreateSchema,
    ConversationModelDeleteSchema,
    ConversationModelSchema,
)


class ConversationModel(object):
    def __init__(self, api_call: ApiCall, model_id: str) -> None:
        self.model_id = model_id
        self.api_call = api_call

    @property
    def _endpoint_path(self) -> str:
        from .conversations_models import ConversationsModels

        return "{0}/{1}".format(ConversationsModels.RESOURCE_PATH, self.model_id)

    def retrieve(self) -> ConversationModelSchema:
        response = self.api_call.get(
            self._endpoint_path,
            as_json=True,
            entity_type=ConversationModelSchema,
        )
        return response

    def update(self, model: ConversationModelCreateSchema) -> ConversationModelSchema:
        response: ConversationModelSchema = self.api_call.put(
            self._endpoint_path,
            body=model,
            entity_type=ConversationModelSchema,
        )
        return response

    def delete(self) -> ConversationModelDeleteSchema:
        response: ConversationModelDeleteSchema = self.api_call.delete(
            self._endpoint_path,
            entity_type=ConversationModelDeleteSchema,
        )
        return response
