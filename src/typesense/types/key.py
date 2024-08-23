"""Types for API keys."""

import sys

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing


_CollectionActions = typing.Literal[
    "collections:list",
    "collections:get",
    "collections:delete",
    "collections:create",
    "collections:*",
]

_DocumentActions = typing.Literal[
    "documents:*",
    "documents:export",
    "documents:import",
    "documents:delete",
    "documents:update",
    "documents:upsert",
    "documents:create",
    "documents:get",
    "documents:search",
]

_AliasActions = typing.Literal[
    "aliases:*",
    "aliases:delete",
    "aliases:create",
    "aliases:get",
    "aliases:list",
]

_SynonymActions = typing.Literal[
    "synonyms:*",
    "synonyms:delete",
    "synonyms:create",
    "synonyms:get",
    "synonyms:list",
]

_OverrideActions = typing.Literal[
    "overrides:*",
    "overrides:delete",
    "overrides:create",
    "overrides:get",
    "overrides:list",
]

_StopwordActions = typing.Literal[
    "stopwords:*",
    "stopwords:delete",
    "stopwords:create",
    "stopwords:get",
    "stopwords:list",
]

_KeyActions = typing.Literal[
    "keys:*",
    "keys:delete",
    "keys:create",
    "keys:get",
    "keys:list",
]

_MiscActions = typing.Literal[
    "*",
    "debug:list",
    "stats.json:list",
    "metrics.json:list",
]

_Actions = typing.Union[
    _CollectionActions,
    _DocumentActions,
    _AliasActions,
    _SynonymActions,
    _OverrideActions,
    _StopwordActions,
    _KeyActions,
    _MiscActions,
]


class ApiKeyCreateSchema(typing.TypedDict):
    """
    Schema for creating a [new API key](https://typesense.org/docs/26.0/api/api-keys.html#create-an-api-key).

    Attributes:
        actions (list[str]): The actions allowed for this key.
        collections (list[str]): The collections this key has access to.
        description (str): The description for this key.
        value (str): The value of the key.
        expires_at (int): The time in UNIX timestamp format when the key will expire.
        autodelete (bool): Whether the key should be deleted after it expires.
    """

    actions: typing.List[_Actions]
    collections: typing.List[str]
    description: str
    value: typing.NotRequired[str]
    expires_at: typing.NotRequired[int]
    autodelete: typing.NotRequired[bool]


class ApiKeyCreateResponseSchema(ApiKeyCreateSchema):
    """
    Response schema for creating a [new API key](https://typesense.org/docs/26.0/api/api-keys.html#create-an-api-key).

    Attributes:
        id (int): The ID of the key.

    Plus all the attributes from `ApiKeyCreateSchema`.
    """

    id: int


class ApiKeySchema(typing.TypedDict):
    """
    Response schema for an [API key](https://typesense.org/docs/26.0/api/api-keys.html#retrieve-an-api-key).

    Attributes:
        actions (list[str]): The actions allowed for this key.
        collections (list[str]): The collections this key has access to.
        description (str): The description for this key.
        id (int): The ID of the key.
        value_prefix (str): The value prefix of the key.
        expires_at (int): The time in UNIX timestamp format when the key
    """

    actions: typing.List[_Actions]
    collections: typing.List[str]
    description: str
    id: int
    value_prefix: str
    expires_at: int


class ApiKeyRetrieveSchema(typing.TypedDict):
    """
    Response schema for retrieving [API keys](https://typesense.org/docs/26.0/api/api-keys.html#list-all-keys).

    Attributes:
        keys (list[ApiKeySchema]): The list of keys.
    """

    keys: typing.List[ApiKeySchema]


class ApiKeyDeleteSchema(typing.TypedDict):
    """
    Response schema for deleting an [API key](https://typesense.org/docs/26.0/api/api-keys.html#delete-api-key).

    Attributes:
        id (int): The ID of the key.
    """

    id: int
