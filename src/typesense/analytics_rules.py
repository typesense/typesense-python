"""Client for Analytics rules collection operations."""

import sys

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

from typesense.analytics_rule import AnalyticsRule
from typesense.api_call import ApiCall
from typesense.types.analytics import (
    AnalyticsRuleCreate,
    AnalyticsRuleSchema,
    AnalyticsRuleUpdate,
)


class AnalyticsRules(object):
    resource_path: typing.Final[str] = "/analytics/rules"

    def __init__(self, api_call: ApiCall) -> None:
        self.api_call = api_call
        self.rules: typing.Dict[str, AnalyticsRuleSchema] = {}

    def __getitem__(self, rule_name: str) -> AnalyticsRuleSchema:
        if rule_name not in self.rules:
            self.rules[rule_name] = AnalyticsRule(self.api_call, rule_name)
        return self.rules[rule_name]

    def create(self, rule: AnalyticsRuleCreate) -> AnalyticsRuleSchema:
        response: AnalyticsRuleSchema = self.api_call.post(
            AnalyticsRules.resource_path,
            body=rule,
            as_json=True,
            entity_type=AnalyticsRuleSchema,
        )
        return response

    def retrieve(
        self, *, rule_tag: typing.Union[str, None] = None
    ) -> typing.List[AnalyticsRuleSchema]:
        params: typing.Dict[str, str] = {}
        if rule_tag:
            params["rule_tag"] = rule_tag
        response: typing.List[AnalyticsRuleSchema] = self.api_call.get(
            AnalyticsRules.resource_path,
            params=params if params else None,
            as_json=True,
            entity_type=typing.List[AnalyticsRuleSchema],
        )
        return response

    def upsert(
        self, rule_name: str, update: AnalyticsRuleUpdate
    ) -> AnalyticsRuleSchema:
        response: AnalyticsRuleSchema = self.api_call.put(
            "/".join([AnalyticsRules.resource_path, rule_name]),
            body=update,
            entity_type=AnalyticsRuleSchema,
        )
        return response
