"""Tests for v30 Analytics Rules endpoints (client.analytics.rules)."""

from __future__ import annotations

import pytest
import requests_mock

from tests.utils.version import is_v30_or_above
from typesense.client import Client
from typesense.analytics_rules import AnalyticsRules
from typesense.analytics_rule import AnalyticsRule
from typesense.types.analytics import AnalyticsRuleCreate


pytestmark = pytest.mark.skipif(
    not is_v30_or_above(
        Client(
            {
                "api_key": "xyz",
                "nodes": [{"host": "localhost", "port": 8108, "protocol": "http"}],
            }
        )
    ),
    reason="Run v30 analytics tests only on v30+",
)


def test_rules_init(fake_api_call) -> None:
    rules = AnalyticsRules(fake_api_call)
    assert rules.rules == {}


def test_rule_getitem(fake_api_call) -> None:
    rules = AnalyticsRules(fake_api_call)
    rule = rules["company_analytics_rule"]
    assert isinstance(rule, AnalyticsRule)
    assert rule._endpoint_path == "/analytics/rules/company_analytics_rule"


def test_rules_create(fake_api_call) -> None:
    rules = AnalyticsRules(fake_api_call)
    body: AnalyticsRuleCreate = {
        "name": "company_analytics_rule",
        "type": "popular_queries",
        "collection": "companies",
        "event_type": "search",
        "params": {"destination_collection": "companies_queries", "limit": 1000},
    }
    with requests_mock.Mocker() as mock:
        mock.post("http://nearest:8108/analytics/rules", json=body)
        resp = rules.create(body)
        assert resp == body


def test_rules_retrieve_with_tag(fake_api_call) -> None:
    rules = AnalyticsRules(fake_api_call)
    with requests_mock.Mocker() as mock:
        mock.get(
            "http://nearest:8108/analytics/rules?rule_tag=homepage",
            json=[{"name": "rule1", "rule_tag": "homepage"}],
        )
        resp = rules.retrieve(rule_tag="homepage")
        assert isinstance(resp, list)
        assert resp[0]["rule_tag"] == "homepage"


def test_rules_upsert(fake_api_call) -> None:
    rules = AnalyticsRules(fake_api_call)
    with requests_mock.Mocker() as mock:
        mock.put(
            "http://nearest:8108/analytics/rules/company_analytics_rule",
            json={"name": "company_analytics_rule"},
        )
        resp = rules.upsert("company_analytics_rule", {"params": {}})
        assert resp["name"] == "company_analytics_rule"


def test_rules_retrieve(fake_api_call) -> None:
    rules = AnalyticsRules(fake_api_call)
    with requests_mock.Mocker() as mock:
        mock.get(
            "http://nearest:8108/analytics/rules",
            json=[{"name": "company_analytics_rule"}],
        )
        resp = rules.retrieve()
        assert isinstance(resp, list)
        assert resp[0]["name"] == "company_analytics_rule"


def test_actual_create(
    actual_analytics_rules: AnalyticsRules,
    delete_all: None,
    delete_all_analytics_rules: None,
    create_collection: None,
    create_query_collection: None,
) -> None:
    body: AnalyticsRuleCreate = {
        "name": "company_analytics_rule",
        "type": "nohits_queries",
        "collection": "companies",
        "event_type": "search",
        "params": {"destination_collection": "companies_queries", "limit": 1000},
    }
    resp = actual_analytics_rules.create(rule=body)
    assert resp["name"] == "company_analytics_rule"
    assert resp["params"]["destination_collection"] == "companies_queries"


def test_actual_update(
    actual_analytics_rules: AnalyticsRules,
    delete_all: None,
    delete_all_analytics_rules: None,
    create_analytics_rule: None,
) -> None:
    resp = actual_analytics_rules.upsert(
        "company_analytics_rule",
        {
            "params": {
                "destination_collection": "companies_queries",
                "limit": 500,
            },
        },
    )
    assert resp["name"] == "company_analytics_rule"


def test_actual_retrieve(
    actual_analytics_rules: AnalyticsRules,
    delete_all: None,
    delete_all_analytics_rules: None,
    create_analytics_rule: None,
) -> None:
    rules = actual_analytics_rules.retrieve()
    assert isinstance(rules, list)
    assert any(r.get("name") == "company_analytics_rule" for r in rules)
