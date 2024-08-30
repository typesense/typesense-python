"""Override types for Typesense Python Client."""

import sys

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing


class OverrideQueryRuleSchema(typing.TypedDict):
    """
    The schema for the rule field in the Overrides.upsert method.

    Attributes:
        query (str): The query string.
        match (typing.Literal['contains', 'exact']): The match type.
        filter_by (str): The filter string.
        tags (list[str]): The tags list.
    """

    query: str
    match: typing.Literal["contains", "exact"]
    filter_by: typing.NotRequired[str]
    tags: typing.NotRequired[typing.List[str]]


class OverrideFilterSchema(typing.TypedDict):
    """
    The schema for the rule field in the Overrides.upsert method.

    Attributes:
        filter_by (str): The filter string.
        tags (list[str]): The tags list.
    """

    filter_by: str
    tags: typing.NotRequired[typing.List[str]]


class IncludesSchema(typing.TypedDict):
    """
    The schema for the includes field in the Overrides.upsert method.

    Attributes:
        id (str): The ID of the document.
        position (int): The position of the ID in the response.
    """

    id: str
    position: int


class OverrideCreateSchema(typing.TypedDict):
    """
    The schema for the request of the Overrides.upsert method.

    Attributes:
        rule (OverrideQueryRuleSchema | OverrideFilterSchema): The rule.
        sort_by (str): The sort by string.
        filter_by (str): The filter by string.
        excludes (list[str]): The excludes list.
        replace_query (str): The replace query string.
        includes (list[IncludesSchema]): The includes list.
        metadata (dict[str, str]): The metadata dictionary.
        filter_curated_hits (bool): Whether to filter curated hits.
        effective_from_ts (int): The effective from timestamp.
        effective_to_ts (int): The effective to timestamp.
        stop_processing (bool): Whether to stop processing.
    """

    rule: typing.Union[OverrideQueryRuleSchema, OverrideFilterSchema]
    sort_by: typing.NotRequired[str]
    filter_by: typing.NotRequired[str]
    excludes: typing.NotRequired[typing.List[str]]
    replace_query: typing.NotRequired[str]
    includes: typing.NotRequired[typing.List[IncludesSchema]]
    metadata: typing.NotRequired[typing.Dict[str, str]]
    filter_curated_hits: typing.NotRequired[bool]
    effective_from_ts: typing.NotRequired[int]
    effective_to_ts: typing.NotRequired[int]
    stop_processing: typing.NotRequired[bool]


class OverrideSchema(OverrideCreateSchema):
    """The schema for the response of the Overrides.upsert method."""

    id: str


class OverrideDeleteSchema(typing.TypedDict):
    """The schema for the response of the Overrides.delete method."""

    id: str


class OverrideRetrieveSchema(typing.TypedDict):
    """The schema for the response of the Overrides.retrieve method."""

    overrides: typing.List[OverrideSchema]
