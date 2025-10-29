"""Unit tests for per-rule AnalyticsRule operations."""

from __future__ import annotations

import pytest
import requests_mock

from tests.utils.version import is_v30_or_above
from typesense.client import Client
from typesense.analytics_rule import AnalyticsRule
from typesense.analytics_rules import AnalyticsRules


pytestmark = pytest.mark.skipif(
    not is_v30_or_above(
        Client(
            {
                "api_key": "xyz",
                "nodes": [{"host": "localhost", "port": 8108, "protocol": "http"}],
            }
        )
    ),
    reason="Run analytics tests only on v30+",
)


def test_rule_retrieve(fake_api_call) -> None:
    rule = AnalyticsRule(fake_api_call, "company_analytics_rule")
    expected = {"name": "company_analytics_rule"}
    with requests_mock.Mocker() as mock:
        mock.get(
            "http://nearest:8108/analytics/rules/company_analytics_rule",
            json=expected,
        )
        resp = rule.retrieve()
        assert resp == expected


def test_rule_delete(fake_api_call) -> None:
    rule = AnalyticsRule(fake_api_call, "company_analytics_rule")
    expected = {"name": "company_analytics_rule"}
    with requests_mock.Mocker() as mock:
        mock.delete(
            "http://nearest:8108/analytics/rules/company_analytics_rule",
            json=expected,
        )
        resp = rule.delete()
        assert resp == expected


def test_actual_rule_retrieve(
    actual_analytics_rules: AnalyticsRules,
    delete_all: None,
    delete_all_analytics_rules: None,
    create_analytics_rule: None,
) -> None:
    resp = actual_analytics_rules["company_analytics_rule"].retrieve()
    assert resp["name"] == "company_analytics_rule"


def test_actual_rule_delete(
    actual_analytics_rules: AnalyticsRules,
    delete_all: None,
    delete_all_analytics_rules: None,
    create_analytics_rule: None,
) -> None:
    resp = actual_analytics_rules["company_analytics_rule"].delete()
    assert resp["name"] == "company_analytics_rule"
