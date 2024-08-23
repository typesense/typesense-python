import sys

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

from typesense.api_call import ApiCall
from typesense.types.analytics_rule import (
    RuleCreateSchemaForQueries,
    RuleSchemaForCounters,
    RuleSchemaForQueries,
    RulesRetrieveSchema,
)

from .analytics_rule import AnalyticsRule


class AnalyticsRules(object):
    RESOURCE_PATH = "/analytics/rules"

    def __init__(self, api_call: ApiCall):
        self.api_call = api_call
        self.rules: typing.Dict[str, AnalyticsRule] = {}

    def __getitem__(self, rule_id: str) -> AnalyticsRule:
        if not self.rules.get(rule_id):
            self.rules[rule_id] = AnalyticsRule(self.api_call, rule_id)

        return self.rules[rule_id]

    def create(
        self,
        rule: typing.Union[RuleSchemaForCounters, RuleCreateSchemaForQueries],
        params: typing.Union[
            typing.Dict[str, typing.Union[str, int, bool]], None
        ] = None,
    ) -> typing.Union[RuleSchemaForCounters, RuleCreateSchemaForQueries]:
        response: typing.Union[RuleSchemaForCounters, RuleCreateSchemaForQueries] = (
            self.api_call.post(
                AnalyticsRules.RESOURCE_PATH,
                body=rule,
                params=params,
                as_json=True,
                entity_type=typing.Union[
                    RuleSchemaForCounters, RuleCreateSchemaForQueries
                ],
            )
        )
        return response

    def upsert(
        self,
        id: str,
        rule: typing.Union[RuleCreateSchemaForQueries, RuleSchemaForCounters],
    ) -> typing.Union[RuleSchemaForCounters, RuleCreateSchemaForQueries]:
        response = self.api_call.put(
            "{0}/{1}".format(AnalyticsRules.RESOURCE_PATH, id),
            body=rule,
            entity_type=typing.Union[RuleSchemaForQueries, RuleSchemaForCounters],
        )
        return typing.cast(
            typing.Union[RuleSchemaForCounters, RuleCreateSchemaForQueries], response
        )

    def retrieve(self) -> RulesRetrieveSchema:
        response: RulesRetrieveSchema = self.api_call.get(
            AnalyticsRules.RESOURCE_PATH,
            as_json=True,
            entity_type=RulesRetrieveSchema,
        )
        return response
