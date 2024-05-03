from .conversation_model import ConversationModel


class ConversationsModels(object):
    RESOURCE_PATH = '/conversations/models'

    def __init__(self, api_call):
        self.api_call = api_call
        self.conversations_models = {}

    def __getitem__(self, model_id):
        if model_id not in self.conversations_models:
            self.conversations_models[model_id] = ConversationModel(self.api_call, model_id)

        return self.conversations_models.get(model_id)

    def create(self, model):
        return self.api_call.post(ConversationsModels.RESOURCE_PATH, model)

    def retrieve(self):
        return self.api_call.get(ConversationsModels.RESOURCE_PATH)
