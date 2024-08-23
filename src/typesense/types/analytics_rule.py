"""Analytics Rule types for Typesense Python Client."""

import sys

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing


class Event(typing.TypedDict):
    """
    Schema for analytics rule [events](https://typesense.org/docs/26.0/api/analytics-query-suggestions.html#analytics-query-suggestions).

    Attributes:
        type (str): The [type](https://typesense.org/docs/26.0/api/analytics-query-suggestions.html#aggregating-multiple-events) of the event.

        - `click`: Tracking clicks against documents returned in search response..
        - `conversion`: The event is a click.
        - `visit`: Tracking page visits to specific documents, useful for recommendations.

        weight (int): The weight of the event.

        name (str): The name of the event.

    """

    type: typing.Literal["click", "conversion", "visit"]
    weight: int
    name: str


class _Source(typing.TypedDict):
    """
    Schema for the source of the analytics rule.

    Attributes:
        collections (list[str]): The list of collections.

        events (list[Event]): The list of events.
    """

    collections: typing.List[str]
    events: typing.NotRequired[typing.List[Event]]


class _SourceForCounters(typing.TypedDict):
    """
    Schema for the source of the analytics rule for counter rules.

    Attributes:
        collections (list[str]): The list of collections.

        events (list[Event]): The list of events.
    """

    collections: typing.List[str]
    events: typing.List[Event]


class _Destination(typing.TypedDict):
    """
    Schema for the destination of the analytics rule.

    Attributes:
        collection (str): The destination collection.

        counter_field (str): The counter field of the collection.
    """

    collection: str
    counter_field: typing.NotRequired[str]


class _DestinationForCounters(typing.TypedDict):
    """
    Schema for the destination of the analytics rule for counter rules.

    Attributes:
        collection (str): The destination collection.

        counter_field (str): The counter field of the collection.
    """

    collection: str
    counter_field: str


class _RuleParams(typing.TypedDict):
    """
    Schema for the analytics rule parameters.

    Attributes:
        source (_Source): The source of the analytics rule.

        expand_query (bool): Whether to expand the query.

        destination (_Destination): The destination of the analytics rule.

        limit (int): The limit of the analytics rule.
    """

    source: _Source
    expand_query: typing.NotRequired[bool]
    destination: _Destination
    limit: typing.NotRequired[int]


class _RuleParamsForCounters(typing.TypedDict):
    """
    Schema for the analytics rule parameters for counter rules.

    Attributes:
        source (_SourceForCounters): The source of the analytics rule.

        destination (_DestinationForCounters): The destination of the analytics rule.

        limit (int): The limit of the analytics
    """

    source: _SourceForCounters
    destination: _DestinationForCounters
    limit: typing.NotRequired[int]


class RuleCreateSchemaForQueries(typing.TypedDict):
    """
    Schema for the request of the AnalyticsRules.create method.

    Attributes:
        type (str): The type of the analytics rule.

        params (AnalyticsRuleParams): The params of the analytics rule.
    """

    type: typing.Literal["popular_queries", "nohits_queries"]
    params: _RuleParams


class RuleCreateSchemaForCounters(typing.TypedDict):
    """
    Schema for the request of the AnalyticsRules.create method.

    Attributes:
        type (str): The type of the analytics rule.

        params (AnalyticsRuleParams): The params of the analytics rule.
    """

    type: typing.Literal["counter"]
    params: _RuleParamsForCounters


class RuleSchemaForQueries(RuleCreateSchemaForQueries):
    """
    Schema for the response of the AnalyticsRules.create method.

    Attributes:
        name (str): The name of the analytics rule.

        type (str): The type of the analytics rule.

        params (AnalyticsRuleParams): The params of the analytics rule.
    """

    name: str


class RuleSchemaForCounters(RuleCreateSchemaForCounters):
    """
    Schema for the response of the AnalyticsRules.create method.

    Attributes:
        name (str): The name of the analytics rule.

        type (str): The type of the analytics rule.

        params (AnalyticsRuleParams): The params of the analytics rule.
    """

    name: str


class RuleDeleteSchema(typing.TypedDict):
    """
    Schema for the response of the AnalyticsRules.delete method.

    Attributes:
        name (str): The name of the analytics rule.
    """

    name: str


class RulesRetrieveSchema(typing.TypedDict):
    """
    Schema for the response of the AnalyticsRules.retrieve method.

    Attributes:
        rules(typing.List[AnalyticsRuleSchema]): The list of analytics rules.
    """

    rules: typing.List[typing.Union[RuleSchemaForQueries, RuleSchemaForCounters]]
