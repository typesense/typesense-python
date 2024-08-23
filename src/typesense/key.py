from typesense.api_call import ApiCall
from typesense.types.key import ApiKeyDeleteSchema, ApiKeySchema


class Key(object):
    def __init__(self, api_call: ApiCall, key_id: int) -> None:
        self.key_id = key_id
        self.api_call = api_call

    @property
    def _endpoint_path(self) -> str:
        from .keys import Keys

        return "{0}/{1}".format(Keys.RESOURCE_PATH, self.key_id)

    def retrieve(self) -> ApiKeySchema:
        response: ApiKeySchema = self.api_call.get(
            self._endpoint_path, as_json=True, entity_type=ApiKeySchema
        )
        return response

    def delete(self) -> ApiKeyDeleteSchema:
        resposne: ApiKeyDeleteSchema = self.api_call.delete(
            self._endpoint_path, entity_type=ApiKeyDeleteSchema
        )
        return resposne
