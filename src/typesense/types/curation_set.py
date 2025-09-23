"""Curation Set types for Typesense Python Client."""

import sys

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing


class CurationIncludeSchema(typing.TypedDict):
    """
    Schema representing an included document for a curation rule.
    """

    id: str
    position: int


class CurationExcludeSchema(typing.TypedDict):
    """
    Schema representing an excluded document for a curation rule.
    """

    id: str


class CurationRuleSchema(typing.TypedDict, total=False):
    """
    Schema representing rule conditions for a curation item.
    """

    query: typing.NotRequired[str]
    match: typing.NotRequired[typing.Literal["exact", "contains"]]
    filter_by: typing.NotRequired[str]
    tags: typing.NotRequired[typing.List[str]]


class CurationItemSchema(typing.TypedDict, total=False):
    """
    Schema for a single curation item (aka CurationObject in the API).
    """

    id: str
    rule: CurationRuleSchema
    includes: typing.NotRequired[typing.List[CurationIncludeSchema]]
    excludes: typing.NotRequired[typing.List[CurationExcludeSchema]]
    filter_by: typing.NotRequired[str]
    sort_by: typing.NotRequired[str]
    replace_query: typing.NotRequired[str]
    remove_matched_tokens: typing.NotRequired[bool]
    filter_curated_hits: typing.NotRequired[bool]
    stop_processing: typing.NotRequired[bool]
    metadata: typing.Dict[str, typing.Any]


class CurationSetUpsertSchema(typing.TypedDict):
    """
    Payload schema to create or replace a curation set.
    """

    items: typing.List[CurationItemSchema]


class CurationSetSchema(CurationSetUpsertSchema):
    """
    Response schema for a curation set.
    """

    name: str


class CurationSetsListEntrySchema(typing.TypedDict):
    """A single entry in the curation sets list response."""

    name: str
    items: typing.List[CurationItemSchema]


class CurationSetsListResponseSchema(typing.List[CurationSetsListEntrySchema]):
    """List response for all curation sets."""


class CurationSetListItemResponseSchema(typing.List[CurationItemSchema]):
    """List response for items under a specific curation set."""


class CurationItemDeleteSchema(typing.TypedDict):
    """Response schema for deleting a curation item."""

    id: str


class CurationSetDeleteSchema(typing.TypedDict):
    """Response schema for deleting a curation set."""

    name: str


