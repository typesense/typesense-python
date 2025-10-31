"""Per-rule client for Analytics rules operations."""

from typesense.api_call import ApiCall
from typesense.types.analytics import AnalyticsRuleSchema


class AnalyticsRule:
    def __init__(self, api_call: ApiCall, rule_name: str) -> None:
        self.api_call = api_call
        self.rule_name = rule_name

    @property
    def _endpoint_path(self) -> str:
        from typesense.analytics_rules import AnalyticsRules

        return "/".join([AnalyticsRules.resource_path, self.rule_name])

    def retrieve(self) -> AnalyticsRuleSchema:
        response: AnalyticsRule = self.api_call.get(
            self._endpoint_path,
            as_json=True,
            entity_type=AnalyticsRule,
        )
        return response

    def delete(self) -> AnalyticsRuleSchema:
        response: AnalyticsRule = self.api_call.delete(
            self._endpoint_path,
            entity_type=AnalyticsRule,
        )
        return response
