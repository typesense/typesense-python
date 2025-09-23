"""Fixtures for Analytics (current) tests."""

import pytest
import requests

from typesense.analytics_rule import AnalyticsRule
from typesense.analytics_rules import AnalyticsRules
from typesense.api_call import ApiCall


@pytest.fixture(scope="function", name="delete_all_analytics_rules")
def clear_typesense_analytics_rules() -> None:
    """Remove all analytics rules from the Typesense server."""
    url = "http://localhost:8108/analytics/rules"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}

    response = requests.get(url, headers=headers, timeout=3)
    response.raise_for_status()
    rules = response.json()

    # v30 returns a list of rule objects
    for rule in rules:
        rule_name = rule.get("name")
        delete_url = f"{url}/{rule_name}"
        delete_response = requests.delete(delete_url, headers=headers, timeout=3)
        delete_response.raise_for_status()


@pytest.fixture(scope="function", name="create_analytics_rule")
def create_analytics_rule_fixture(
    create_collection: None,
    create_query_collection: None,
) -> None:
    """Create an analytics rule in the Typesense server."""
    url = "http://localhost:8108/analytics/rules"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}
    analytics_rule_data = {
        "name": "company_analytics_rule",
        "type": "nohits_queries",
        "collection": "companies",
        "event_type": "search",
        "params": {
            "destination_collection": "companies_queries",
            "limit": 1000,
        },
    }

    response = requests.post(url, headers=headers, json=analytics_rule_data, timeout=3)
    response.raise_for_status()


@pytest.fixture(scope="function", name="fake_analytics_rules")
def fake_analytics_rules_fixture(fake_api_call: ApiCall) -> AnalyticsRules:
    """Return an AnalyticsRules object with test values."""
    return AnalyticsRules(fake_api_call)


@pytest.fixture(scope="function", name="actual_analytics_rules")
def actual_analytics_rules_fixture(actual_api_call: ApiCall) -> AnalyticsRules:
    """Return an AnalyticsRules object using a real API."""
    return AnalyticsRules(actual_api_call)


@pytest.fixture(scope="function", name="fake_analytics_rule")
def fake_analytics_rule_fixture(fake_api_call: ApiCall) -> AnalyticsRule:
    """Return an AnalyticsRule object with test values."""
    return AnalyticsRule(fake_api_call, "company_analytics_rule")

@pytest.fixture(scope="function", name="create_query_collection")
def create_query_collection_fixture() -> None:
    """Create a query collection for analytics rules in the Typesense server."""
    url = "http://localhost:8108/collections"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}
    query_collection_data = {
        "name": "companies_queries",
        "fields": [
            {
                "name": "q",
                "type": "string",
            },
            {
                "name": "count",
                "type": "int32",
            },
        ],
    }

    response = requests.post(
        url,
        headers=headers,
        json=query_collection_data,
        timeout=3,
    )
    response.raise_for_status()