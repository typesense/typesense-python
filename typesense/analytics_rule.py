class AnalyticsRule(object):
    def __init__(self, api_call, rule_id):
        self.api_call = api_call
        self.rule_id = rule_id

    def _endpoint_path(self):
        from .analytics_rules import AnalyticsRules
        return u"{0}/{1}".format(AnalyticsRules.RESOURCE_PATH, self.rule_id)

    def retrieve(self):
        return self.api_call.get(self._endpoint_path())

    def delete(self):
        return self.api_call.delete(self._endpoint_path())
