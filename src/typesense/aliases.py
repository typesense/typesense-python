from typesense.alias import Alias
from typesense.api_call import ApiCall
from typesense.types.alias import AliasCreateSchema, AliasesResponseSchema, AliasSchema


class Aliases:
    RESOURCE_PATH = "/aliases"

    def __init__(self, api_call: ApiCall):
        self.api_call = api_call
        self.aliases: dict[str, Alias] = {}

    def __getitem__(self, name: str) -> Alias:
        if not self.aliases.get(name):
            self.aliases[name] = Alias(self.api_call, name)

        return self.aliases.get(name)

    def _endpoint_path(self, alias_name: str) -> str:
        return "{0}/{1}".format(Aliases.RESOURCE_PATH, alias_name)

    def upsert(self, name: str, mapping: AliasCreateSchema) -> AliasSchema:
        response: AliasSchema = self.api_call.put(
            self._endpoint_path(name),
            body=mapping,
            entity_type=AliasSchema,
        )

        return response

    def retrieve(self) -> AliasesResponseSchema:
        response: AliasesResponseSchema = self.api_call.get(
            Aliases.RESOURCE_PATH,
            as_json=True,
            entity_type=AliasesResponseSchema,
        )
        return response
