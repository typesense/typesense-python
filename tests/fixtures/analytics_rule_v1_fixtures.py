"""Fixtures for the Analytics Rules V1 tests."""

import pytest
import requests

from typesense.analytics_rule_v1 import AnalyticsRuleV1
from typesense.analytics_rules_v1 import AnalyticsRulesV1
from typesense.api_call import ApiCall


@pytest.fixture(scope="function", name="delete_all_analytics_rules_v1")
def clear_typesense_analytics_rules_v1() -> None:
    """Remove all analytics_rules from the Typesense server."""
    url = "http://localhost:8108/analytics/rules"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}

    # Get the list of rules
    response = requests.get(url, headers=headers, timeout=3)
    response.raise_for_status()
    analytics_rules = response.json()

    # Delete each analytics_rule
    for analytics_rule_set in analytics_rules["rules"]:
        analytics_rule_id = analytics_rule_set.get("name")
        delete_url = f"{url}/{analytics_rule_id}"
        delete_response = requests.delete(delete_url, headers=headers, timeout=3)
        delete_response.raise_for_status()


@pytest.fixture(scope="function", name="create_analytics_rule_v1")
def create_analytics_rule_v1_fixture(
    create_collection: None,
    create_query_collection: None,
) -> None:
    """Create a collection in the Typesense server."""
    url = "http://localhost:8108/analytics/rules"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}
    analytics_rule_data = {
        "name": "company_analytics_rule",
        "type": "nohits_queries",
        "params": {
            "source": {
                "collections": ["companies"],
            },
            "destination": {"collection": "companies_queries"},
        },
    }

    response = requests.post(url, headers=headers, json=analytics_rule_data, timeout=3)
    response.raise_for_status()


@pytest.fixture(scope="function", name="fake_analytics_rules_v1")
def fake_analytics_rules_v1_fixture(fake_api_call: ApiCall) -> AnalyticsRulesV1:
    """Return a AnalyticsRule object with test values."""
    return AnalyticsRulesV1(fake_api_call)


@pytest.fixture(scope="function", name="actual_analytics_rules_v1")
def actual_analytics_rules_v1_fixture(actual_api_call: ApiCall) -> AnalyticsRulesV1:
    """Return a AnalyticsRules object using a real API."""
    return AnalyticsRulesV1(actual_api_call)


@pytest.fixture(scope="function", name="fake_analytics_rule_v1")
def fake_analytics_rule_v1_fixture(fake_api_call: ApiCall) -> AnalyticsRuleV1:
    """Return a AnalyticsRule object with test values."""
    return AnalyticsRuleV1(fake_api_call, "company_analytics_rule")


