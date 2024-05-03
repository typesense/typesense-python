class ConversationModel(object):
    def __init__(self, api_call, model_id):
        self.model_id = model_id
        self.api_call = api_call

    def _endpoint_path(self):
        from .conversations_models import ConversationsModels
        return u"{0}/{1}".format(ConversationsModels.RESOURCE_PATH, self.model_id)

    def retrieve(self):
        return self.api_call.get(self._endpoint_path())

    def update(self, model):
        return self.api_call.put(self._endpoint_path(), model)

    def delete(self):
        return self.api_call.delete(self._endpoint_path())
