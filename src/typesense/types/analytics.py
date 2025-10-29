"""Types for Analytics endpoints and Analytics Rules."""

import sys

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing


class AnalyticsEvent(typing.TypedDict):
    """Schema for an analytics event to be created."""

    name: str
    data: typing.Dict[str, typing.Any]


class AnalyticsEventCreateResponse(typing.TypedDict):
    """Response schema for creating an analytics event and for flush."""

    ok: bool


class _AnalyticsEventItem(typing.TypedDict, total=False):
    name: str
    collection: str
    timestamp: typing.NotRequired[int]
    user_id: str
    doc_id: typing.NotRequired[str]
    doc_ids: typing.NotRequired[typing.List[str]]
    query: typing.NotRequired[str]


class AnalyticsEventsResponse(typing.TypedDict):
    """Response schema for retrieving analytics events."""

    events: typing.List[_AnalyticsEventItem]


class AnalyticsStatus(typing.TypedDict, total=False):
    """Response schema for analytics status."""

    popular_prefix_queries: int
    nohits_prefix_queries: int
    log_prefix_queries: int
    query_log_events: int
    query_counter_events: int
    doc_log_events: int
    doc_counter_events: int


# Rules


class AnalyticsRuleParams(typing.TypedDict, total=False):
    destination_collection: typing.NotRequired[str]
    limit: typing.NotRequired[int]
    capture_search_requests: typing.NotRequired[bool]
    meta_fields: typing.NotRequired[typing.List[str]]
    expand_query: typing.NotRequired[bool]
    counter_field: typing.NotRequired[str]
    weight: typing.NotRequired[int]


class AnalyticsRuleCreate(typing.TypedDict):
    name: str
    type: str
    collection: str
    event_type: str
    params: typing.NotRequired[AnalyticsRuleParams]
    rule_tag: typing.NotRequired[str]


class AnalyticsRuleUpdate(typing.TypedDict, total=False):
    name: str
    rule_tag: str
    params: AnalyticsRuleParams


class AnalyticsRuleSchema(AnalyticsRuleCreate, total=False):
    pass
