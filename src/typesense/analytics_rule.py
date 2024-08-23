import sys

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

from typesense.api_call import ApiCall
from typesense.types.analytics_rule import (
    RuleDeleteSchema,
    RuleSchemaForCounters,
    RuleSchemaForQueries,
)


class AnalyticsRule(object):
    def __init__(self, api_call: ApiCall, rule_id: str):
        self.api_call = api_call
        self.rule_id = rule_id

    @property
    def _endpoint_path(self) -> str:
        from .analytics_rules import AnalyticsRules

        return "{0}/{1}".format(AnalyticsRules.RESOURCE_PATH, self.rule_id)

    def retrieve(
        self,
    ) -> typing.Union[RuleSchemaForQueries, RuleSchemaForCounters]:
        response: typing.Union[RuleSchemaForQueries, RuleSchemaForCounters] = (
            self.api_call.get(
                self._endpoint_path,
                entity_type=typing.Union[RuleSchemaForQueries, RuleSchemaForCounters],
                as_json=True,
            )
        )
        return response

    def delete(self) -> RuleDeleteSchema:
        response: RuleDeleteSchema = self.api_call.delete(
            self._endpoint_path, entity_type=RuleDeleteSchema
        )
        return response
