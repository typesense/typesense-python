"""Types for Analytics endpoints and Analytics Rules."""

import sys

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing


class AnalyticsEvent(typing.TypedDict):
    """Schema for an analytics event to be created."""

    name: str
    event_type: str
    data: typing.Dict[str, typing.Any]


class AnalyticsEventCreateResponse(typing.TypedDict):
    """Response schema for creating an analytics event and for flush."""

    ok: bool


class _AnalyticsEventItem(typing.TypedDict, total=False):
    name: str
    event_type: str
    collection: str
    timestamp: int
    user_id: str
    doc_id: str
    doc_ids: typing.List[str]
    query: str


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
    destination_collection: str
    limit: int
    capture_search_requests: bool
    meta_fields: typing.List[str]
    expand_query: bool
    counter_field: str
    weight: int


class AnalyticsRuleCreate(typing.TypedDict):
    name: str
    type: str
    collection: str
    event_type: str
    params: AnalyticsRuleParams
    rule_tag: typing.NotRequired[str]


class AnalyticsRuleUpdate(typing.TypedDict, total=False):
    name: str
    rule_tag: str
    params: AnalyticsRuleParams


class AnalyticsRule(AnalyticsRuleCreate, total=False):
    pass


