from typesense.api_call import ApiCall

from .analytics_rules import AnalyticsRules


class Analytics(object):
    def __init__(self, api_call: ApiCall) -> None:
        self.rules = AnalyticsRules(api_call)
