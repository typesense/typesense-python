from typesense.api_call import ApiCall
from typesense.types.alias import AliasSchema


class Alias(object):
    def __init__(self, api_call: ApiCall, name: str):
        self.api_call = api_call
        self.name = name

    @property
    def _endpoint_path(self) -> str:
        from .aliases import Aliases

        return "{0}/{1}".format(Aliases.RESOURCE_PATH, self.name)

    def retrieve(self) -> AliasSchema:
        response: AliasSchema = self.api_call.get(
            self._endpoint_path, entity_type=AliasSchema, as_json=True
        )
        return response

    def delete(self) -> AliasSchema:
        response = self.api_call.delete(self._endpoint_path, entity_type=AliasSchema)

        return response
