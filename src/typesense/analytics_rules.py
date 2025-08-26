"""Client for Analytics rules collection operations."""

import sys

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

from typesense.api_call import ApiCall
from typesense.types.analytics import (
    AnalyticsRule,
    AnalyticsRuleCreate,
    AnalyticsRuleUpdate,
)


class AnalyticsRules(object):
    resource_path: typing.Final[str] = "/analytics/rules"

    def __init__(self, api_call: ApiCall) -> None:
        self.api_call = api_call
        self.rules: typing.Dict[str, "AnalyticsRule"] = {}

    def __getitem__(self, rule_name: str) -> "AnalyticsRule":
        if rule_name not in self.rules:
            from typesense.analytics_rule import AnalyticsRule as PerRule

            self.rules[rule_name] = PerRule(self.api_call, rule_name)
        return typing.cast("AnalyticsRule", self.rules[rule_name])

    def create(self, rule: AnalyticsRuleCreate) -> AnalyticsRule:
        response: AnalyticsRule = self.api_call.post(
            AnalyticsRules.resource_path,
            body=rule,
            as_json=True,
            entity_type=AnalyticsRule,
        )
        return response

    def retrieve(self, *, rule_tag: typing.Union[str, None] = None) -> typing.List[AnalyticsRule]:
        params: typing.Dict[str, str] = {}
        if rule_tag:
            params["rule_tag"] = rule_tag
        response: typing.List[AnalyticsRule] = self.api_call.get(
            AnalyticsRules.resource_path,
            params=params if params else None,
            as_json=True,
            entity_type=typing.List[AnalyticsRule],
        )
        return response

    def upsert(self, rule_name: str, update: AnalyticsRuleUpdate) -> AnalyticsRule:
        response: AnalyticsRule = self.api_call.put(
            "/".join([AnalyticsRules.resource_path, rule_name]),
            body=update,
            entity_type=AnalyticsRule,
        )
        return response