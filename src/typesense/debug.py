from typesense.api_call import ApiCall
from typesense.types.debug import DebugResponseSchema


class Debug(object):
    RESOURCE_PATH = "/debug"

    def __init__(self, api_call: ApiCall) -> None:
        self.api_call = api_call

    def retrieve(self) -> DebugResponseSchema:
        return self.api_call.get(
            "{0}".format(Debug.RESOURCE_PATH),
            as_json=True,
            entity_type=DebugResponseSchema,
        )
