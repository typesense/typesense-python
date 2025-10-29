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


class CurationRuleTagsSchema(typing.TypedDict):
    """
    Schema for a curation rule using tags.
    """

    tags: typing.List[str]


class CurationRuleQuerySchema(typing.TypedDict):
    """
    Schema for a curation rule using query and match.
    """

    query: str
    match: typing.Literal["exact", "contains"]


class CurationRuleFilterBySchema(typing.TypedDict):
    """
    Schema for a curation rule using filter_by.
    """

    filter_by: str


CurationRuleSchema = typing.Union[
    CurationRuleTagsSchema,
    CurationRuleQuerySchema,
    CurationRuleFilterBySchema,
]
"""
Schema representing rule conditions for a curation item.

A curation rule must be exactly one of:
- A tags-based rule: `{ tags: string[] }`
- A query-based rule: `{ query: string; match: "exact" | "contains" }`
- A filter_by-based rule: `{ filter_by: string }`
"""


class CurationItemSchema(typing.TypedDict):
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
    effective_from_ts: typing.NotRequired[int]
    effective_to_ts: typing.NotRequired[int]
    metadata: typing.NotRequired[typing.Dict[str, typing.Any]]


class CurationSetUpsertSchema(typing.TypedDict):
    """
    Payload schema to create or replace a curation set.
    """

    items: typing.List[CurationItemSchema]


class CurationSetSchema(CurationSetUpsertSchema, total=False):
    """
    Response schema for a curation set.
    """

    name: typing.NotRequired[str]


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


