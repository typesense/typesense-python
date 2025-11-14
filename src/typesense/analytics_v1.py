"""
This module provides functionality for managing analytics (V1) in Typesense.

Classes:
    - AnalyticsV1: Handles operations related to analytics, including access to analytics rules.

Methods:
    - __init__: Initializes the AnalyticsV1 object.

The AnalyticsV1 class serves as an entry point for analytics-related operations in Typesense,
currently providing access to AnalyticsRulesV1.

For more information on analytics, refer to the Analytics & Query Suggestion
[documentation](https://typesense.org/docs/27.0/api/analytics-query-suggestions.html)

This module uses type hinting and is compatible with Python 3.11+ as well as earlier
versions through the use of the typing_extensions library.
"""

from typing_extensions import deprecated

from typesense.analytics_rules_v1 import AnalyticsRulesV1
from typesense.api_call import ApiCall


@deprecated("AnalyticsV1 is deprecated on v30+. Use client.analytics instead.")
class AnalyticsV1(object):
    """
    Class for managing analytics in Typesense (V1).

    This class provides access to analytics-related functionalities,
    currently including operations on analytics rules.

    Attributes:
        rules (AnalyticsRulesV1): An instance of AnalyticsRulesV1 for managing analytics rules.
    """

    def __init__(self, api_call: ApiCall) -> None:
        """
        Initialize the AnalyticsV1 object.

        Args:
            api_call (ApiCall): The API call object for making requests.
        """
        self._rules = AnalyticsRulesV1(api_call)

    @property
    def rules(self) -> AnalyticsRulesV1:
        return self._rules


