from .analytics_rules import AnalyticsRules


class Analytics(object):
    def __init__(self, api_call):
        self.rules = AnalyticsRules(api_call)
