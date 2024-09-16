"""
This module provides functionality for managing analytics in Typesense.

Classes:
    - Analytics: Handles operations related to analytics, including access to analytics rules.

Methods:
    - __init__: Initializes the Analytics object.

The Analytics class serves as an entry point for analytics-related operations in Typesense,
currently providing access to AnalyticsRules.

For more information on analytics, refer to the Analytics & Query Suggestion
[documentation](https://typesense.org/docs/27.0/api/analytics-query-suggestions.html)

This module uses type hinting and is compatible with Python 3.11+ as well as earlier
versions through the use of the typing_extensions library.
"""

from typesense.analytics_rules import AnalyticsRules
from typesense.api_call import ApiCall


class Analytics(object):
    """
    Class for managing analytics in Typesense.

    This class provides access to analytics-related functionalities,
    currently including operations on analytics rules.

    Attributes:
        rules (AnalyticsRules): An instance of AnalyticsRules for managing analytics rules.
    """

    def __init__(self, api_call: ApiCall) -> None:
        """
        Initialize the Analytics object.

        Args:
            api_call (ApiCall): The API call object for making requests.
        """
        self.rules = AnalyticsRules(api_call)
