"""
This module provides functionality for managing analytics rules in Typesense (V1).

Classes:
    - AnalyticsRulesV1: Handles operations related to analytics rules.

Methods:
    - __init__: Initializes the AnalyticsRulesV1 object.
    - __getitem__: Retrieves or creates an AnalyticsRuleV1 object for a given rule_id.
    - create: Creates a new analytics rule.
    - upsert: Creates or updates an analytics rule.
    - retrieve: Retrieves all analytics rules.

Attributes:
    - resource_path: The API resource path for analytics rules.

The AnalyticsRulesV1 class interacts with the Typesense API to manage analytics rule operations.
It provides methods to create, update, and retrieve analytics rules, as well as access
individual AnalyticsRuleV1 objects.

For more information on analytics, refer to the Analytics & Query Suggestion
[documentation](https://typesense.org/docs/27.0/api/analytics-query-suggestions.html)

This module uses type hinting and is compatible with Python 3.11+ as well as earlier
versions through the use of the typing_extensions library.
"""

import sys

from typesense.logger import warn_deprecation

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

from typesense.analytics_rule_v1 import AnalyticsRuleV1
from typesense.api_call import ApiCall
from typesense.types.analytics_rule_v1 import (
    RuleCreateSchemaForCounters,
    RuleCreateSchemaForQueries,
    RuleSchemaForCounters,
    RuleSchemaForQueries,
    RulesRetrieveSchema,
)

_RuleParams = typing.Union[
    typing.Dict[str, typing.Union[str, int, bool]],
    None,
]


class AnalyticsRulesV1(object):
    """
    Class for managing analytics rules in Typesense (V1).

    This class provides methods to interact with analytics rules, including
    creating, updating, and retrieving them.

    Attributes:
        resource_path (str): The API resource path for analytics rules.
        api_call (ApiCall): The API call object for making requests.
        rules (Dict[str, AnalyticsRuleV1]): A dictionary of AnalyticsRuleV1 objects.
    """

    resource_path: typing.Final[str] = "/analytics/rules"

    @warn_deprecation(  # type: ignore[misc]
        "AnalyticsRulesV1 is deprecated on v30+. Use client.analytics instead.",
        flag_name="analytics_rules_v1_deprecation",
    )
    def __init__(self, api_call: ApiCall):
        """
        Initialize the AnalyticsRulesV1 object.

        Args:
            api_call (ApiCall): The API call object for making requests.
        """
        self.api_call = api_call
        self.rules: typing.Dict[str, AnalyticsRuleV1] = {}

    def __getitem__(self, rule_id: str) -> AnalyticsRuleV1:
        """
        Get or create an AnalyticsRuleV1 object for a given rule_id.

        Args:
            rule_id (str): The ID of the analytics rule.

        Returns:
            AnalyticsRuleV1: The AnalyticsRuleV1 object for the given ID.
        """
        if not self.rules.get(rule_id):
            self.rules[rule_id] = AnalyticsRuleV1(self.api_call, rule_id)
        return self.rules[rule_id]

    def create(
        self,
        rule: typing.Union[RuleCreateSchemaForCounters, RuleCreateSchemaForQueries],
        rule_parameters: _RuleParams = None,
    ) -> typing.Union[RuleSchemaForCounters, RuleSchemaForQueries]:
        """
        Create a new analytics rule.

        This method can create both counter rules and query rules.

        Args:
            rule (Union[RuleCreateSchemaForCounters, RuleCreateSchemaForQueries]):
                The rule schema. Use RuleCreateSchemaForCounters for counter rules
                and RuleCreateSchemaForQueries for query rules.

            rule_parameters (_RuleParams, optional): Additional rule parameters.

        Returns:
            Union[RuleSchemaForCounters, RuleSchemaForQueries]:
                The created rule. Returns RuleSchemaForCounters for counter rules
                and RuleSchemaForQueries for query rules.
        """
        response: typing.Union[RuleSchemaForCounters, RuleSchemaForQueries] = (
            self.api_call.post(
                AnalyticsRulesV1.resource_path,
                body=rule,
                params=rule_parameters,
                as_json=True,
                entity_type=typing.Union[
                    RuleSchemaForCounters,
                    RuleSchemaForQueries,
                ],
            )
        )
        return response

    def upsert(
        self,
        rule_id: str,
        rule: typing.Union[RuleCreateSchemaForQueries, RuleSchemaForCounters],
    ) -> typing.Union[RuleSchemaForCounters, RuleCreateSchemaForQueries]:
        """
        Create or update an analytics rule.

        Args:
            rule_id (str): The ID of the rule to upsert.
            rule (Union[RuleCreateSchemaForQueries, RuleSchemaForCounters]): The rule schema.

        Returns:
            Union[RuleSchemaForCounters, RuleCreateSchemaForQueries]: The upserted rule.
        """
        response = self.api_call.put(
            "/".join([AnalyticsRulesV1.resource_path, rule_id]),
            body=rule,
            entity_type=typing.Union[RuleSchemaForQueries, RuleSchemaForCounters],
        )
        return typing.cast(
            typing.Union[RuleSchemaForCounters, RuleCreateSchemaForQueries],
            response,
        )

    def retrieve(self) -> RulesRetrieveSchema:
        """
        Retrieve all analytics rules.

        Returns:
            RulesRetrieveSchema: The schema containing all analytics rules.
        """
        response: RulesRetrieveSchema = self.api_call.get(
            AnalyticsRulesV1.resource_path,
            as_json=True,
            entity_type=RulesRetrieveSchema,
        )
        return response
