"""
This module provides functionality for managing individual analytics rules in Typesense.

Classes:
    - AnalyticsRule: Handles operations related to a specific analytics rule.

Methods:
    - __init__: Initializes the AnalyticsRule object.
    - _endpoint_path: Constructs the API endpoint path for this specific analytics rule.
    - retrieve: Retrieves the details of this specific analytics rule.
    - delete: Deletes this specific analytics rule.

The AnalyticsRule class interacts with the Typesense API to manage operations on a
specific analytics rule. It provides methods to retrieve and delete individual rules.

For more information on analytics, refer to the Analytics & Query Suggestion
[documentation](https://typesense.org/docs/27.0/api/analytics-query-suggestions.html)

This module uses type hinting and is compatible with Python 3.11+ as well as earlier
versions through the use of the typing_extensions library.
"""

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


class AnalyticsRule:
    """
    Class for managing individual analytics rules in Typesense.

    This class provides methods to interact with a specific analytics rule,
    including retrieving and deleting it.

    Attributes:
        api_call (ApiCall): The API call object for making requests.
        rule_id (str): The ID of the analytics rule.
    """

    def __init__(self, api_call: ApiCall, rule_id: str):
        """
        Initialize the AnalyticsRule object.

        Args:
            api_call (ApiCall): The API call object for making requests.
            rule_id (str): The ID of the analytics rule.
        """
        self.api_call = api_call
        self.rule_id = rule_id

    def retrieve(
        self,
    ) -> typing.Union[RuleSchemaForQueries, RuleSchemaForCounters]:
        """
        Retrieve this specific analytics rule.

        Returns:
            Union[RuleSchemaForQueries, RuleSchemaForCounters]:
              The schema containing the rule details.
        """
        response: typing.Union[RuleSchemaForQueries, RuleSchemaForCounters] = (
            self.api_call.get(
                self._endpoint_path,
                entity_type=typing.Union[RuleSchemaForQueries, RuleSchemaForCounters],
                as_json=True,
            )
        )
        return response

    def delete(self) -> RuleDeleteSchema:
        """
        Delete this specific analytics rule.

        Returns:
            RuleDeleteSchema: The schema containing the deletion response.
        """
        response: RuleDeleteSchema = self.api_call.delete(
            self._endpoint_path,
            entity_type=RuleDeleteSchema,
        )

        return response

    @property
    def _endpoint_path(self) -> str:
        """
        Construct the API endpoint path for this specific analytics rule.

        Returns:
            str: The constructed endpoint path.
        """
        from typesense.analytics_rules import AnalyticsRules

        return "/".join([AnalyticsRules.resource_path, self.rule_id])
