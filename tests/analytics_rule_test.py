"""Tests for the AnalyticsRule class."""

from __future__ import annotations

import requests_mock

from tests.utils.object_assertions import assert_match_object, assert_object_lists_match
from typesense.analytics_rule import AnalyticsRule
from typesense.analytics_rules import AnalyticsRules
from typesense.api_call import ApiCall
from typesense.types.analytics_rule import RuleDeleteSchema, RuleSchemaForQueries


def test_init(fake_api_call: ApiCall) -> None:
    """Test that the AnalyticsRule object is initialized correctly."""
    analytics_rule = AnalyticsRule(fake_api_call, "company_analytics_rule")

    assert analytics_rule.rule_id == "company_analytics_rule"
    assert_match_object(analytics_rule.api_call, fake_api_call)
    assert_object_lists_match(analytics_rule.api_call.nodes, fake_api_call.nodes)
    assert_match_object(
        analytics_rule.api_call.config.nearest_node,
        fake_api_call.config.nearest_node,
    )
    assert (
        analytics_rule._endpoint_path  # noqa: WPS437
        == "/analytics/rules/company_analytics_rule"
    )


def test_retrieve(fake_analytics_rule: AnalyticsRule) -> None:
    """Test that the AnalyticsRule object can retrieve an analytics_rule."""
    json_response: RuleSchemaForQueries = {
        "name": "company_analytics_rule",
        "params": {
            "destination": {
                "collection": "companies_queries",
            },
            "source": {"collections": ["companies"]},
        },
        "type": "nohits_queries",
    }

    with requests_mock.Mocker() as mock:
        mock.get(
            "/analytics/rules/company_analytics_rule",
            json=json_response,
        )

        response = fake_analytics_rule.retrieve()

        assert len(mock.request_history) == 1
        assert mock.request_history[0].method == "GET"
        assert (
            mock.request_history[0].url
            == "http://nearest:8108/analytics/rules/company_analytics_rule"
        )
        assert response == json_response


def test_delete(fake_analytics_rule: AnalyticsRule) -> None:
    """Test that the AnalyticsRule object can delete an analytics_rule."""
    json_response: RuleDeleteSchema = {
        "name": "company_analytics_rule",
    }
    with requests_mock.Mocker() as mock:
        mock.delete(
            "/analytics/rules/company_analytics_rule",
            json=json_response,
        )

        response = fake_analytics_rule.delete()

        assert len(mock.request_history) == 1
        assert mock.request_history[0].method == "DELETE"
        assert (
            mock.request_history[0].url
            == "http://nearest:8108/analytics/rules/company_analytics_rule"
        )
        assert response == json_response


def test_actual_retrieve(
    actual_analytics_rules: AnalyticsRules,
    delete_all: None,
    delete_all_analytics_rules: None,
    create_analytics_rule: None,
) -> None:
    """Test that the AnalyticsRule object can retrieve a rule from Typesense Server."""
    response = actual_analytics_rules["company_analytics_rule"].retrieve()

    expected: RuleSchemaForQueries = {
        "name": "company_analytics_rule",
        "params": {
            "destination": {"collection": "companies_queries"},
            "limit": 1000,
            "source": {"collections": ["companies"]},
        },
        "type": "nohits_queries",
    }

    assert response == expected


def test_actual_delete(
    actual_analytics_rules: AnalyticsRules,
    delete_all: None,
    delete_all_analytics_rules: None,
    create_analytics_rule: None,
) -> None:
    """Test that the AnalyticsRule object can delete a rule from Typesense Server."""
    response = actual_analytics_rules["company_analytics_rule"].delete()

    expected: RuleDeleteSchema = {
        "name": "company_analytics_rule",
    }
    assert response == expected
