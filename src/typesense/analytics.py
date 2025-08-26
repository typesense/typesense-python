"""Client for Typesense Analytics module."""

import sys

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

from typesense.api_call import ApiCall
from typesense.analytics_events import AnalyticsEvents
from typesense.analytics_rules import AnalyticsRules


class Analytics:
    """Client for v30 Analytics endpoints."""

    def __init__(self, api_call: ApiCall) -> None:
        self.api_call = api_call
        self.rules = AnalyticsRules(api_call)
        self.events = AnalyticsEvents(api_call)



