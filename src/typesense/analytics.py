"""Client for Typesense Analytics module."""

from typesense.analytics_events import AnalyticsEvents
from typesense.analytics_rules import AnalyticsRules
from typesense.api_call import ApiCall


class Analytics:
    """Client for v30 Analytics endpoints."""

    def __init__(self, api_call: ApiCall) -> None:
        self.api_call = api_call
        self.rules = AnalyticsRules(api_call)
        self.events = AnalyticsEvents(api_call)
