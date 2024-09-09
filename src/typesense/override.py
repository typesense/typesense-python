from typesense.api_call import ApiCall
from typesense.types.override import OverrideDeleteSchema, OverrideSchema


class Override:
    def __init__(
        self, api_call: ApiCall, collection_name: str, override_id: str
    ) -> None:
        self.api_call = api_call
        self.collection_name = collection_name
        self.override_id = override_id

    def _endpoint_path(self) -> str:
        from typesense.collections import Collections
        from typesense.overrides import Overrides

        return "{0}/{1}/{2}/{3}".format(
            Collections.RESOURCE_PATH,
            self.collection_name,
            Overrides.RESOURCE_PATH,
            self.override_id,
        )

    def retrieve(self) -> OverrideSchema:
        response: OverrideSchema = self.api_call.get(
            self._endpoint_path(), entity_type=OverrideSchema, as_json=True
        )
        return response

    def delete(self) -> OverrideDeleteSchema:
        response: OverrideDeleteSchema = self.api_call.delete(
            self._endpoint_path(), entity_type=OverrideDeleteSchema
        )
        return response
