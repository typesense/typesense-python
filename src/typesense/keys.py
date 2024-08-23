import base64
import hashlib
import hmac
import json
import sys

from typesense import key
from typesense.api_call import ApiCall
from typesense.types.document import GenerateScopedSearchKeyParams
from typesense.types.key import (
    ApiKeyCreateResponseSchema,
    ApiKeyCreateSchema,
    ApiKeyRetrieveSchema,
    ApiKeySchema,
)

from .key import Key

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing


class Keys(object):
    RESOURCE_PATH = "/keys"

    def __init__(self, api_call: ApiCall) -> None:
        self.api_call = api_call
        self.keys: typing.Dict[int, Key] = {}

    def __getitem__(self, key_id: int) -> Key:
        if not self.keys.get(key_id):
            self.keys[key_id] = Key(self.api_call, key_id)

        return self.keys[key_id]

    def create(self, schema: ApiKeyCreateSchema) -> ApiKeyCreateResponseSchema:
        response: ApiKeySchema = self.api_call.post(
            Keys.RESOURCE_PATH, as_json=True, body=schema, entity_type=ApiKeySchema
        )
        return response

    def generate_scoped_search_key(
        self, search_key: str, parameters: GenerateScopedSearchKeyParams
    ) -> bytes:
        # Note: only a key generated with the `documents:search` action will be accepted by the server
        params_str = json.dumps(parameters)
        digest = base64.b64encode(
            hmac.new(
                search_key.encode("utf-8"),
                params_str.encode("utf-8"),
                digestmod=hashlib.sha256,
            ).digest()
        )
        key_prefix = search_key[0:4]
        raw_scoped_key = "{}{}{}".format(digest.decode("utf-8"), key_prefix, params_str)
        return base64.b64encode(raw_scoped_key.encode("utf-8"))

    def retrieve(self) -> ApiKeyRetrieveSchema:
        response: ApiKeyRetrieveSchema = self.api_call.get(
            Keys.RESOURCE_PATH, entity_type=ApiKeyRetrieveSchema, as_json=True
        )
        return response
