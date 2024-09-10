"""Tests for the AnalyticsRules class."""

from __future__ import annotations

import requests_mock

from tests.utils.object_assertions import assert_match_object, assert_object_lists_match
from typesense.analytics_rules import AnalyticsRules
from typesense.api_call import ApiCall
from typesense.types.analytics_rule import (
    RuleCreateSchemaForQueries,
    RulesRetrieveSchema,
)


def test_init(fake_api_call: ApiCall) -> None:
    """Test that the AnalyticsRules object is initialized correctly."""
    analytics_rules = AnalyticsRules(fake_api_call)

    assert_match_object(analytics_rules.api_call, fake_api_call)
    assert_object_lists_match(
        analytics_rules.api_call.node_manager.nodes,
        fake_api_call.node_manager.nodes,
    )
    assert_match_object(
        analytics_rules.api_call.config.nearest_node,
        fake_api_call.config.nearest_node,
    )

    assert not analytics_rules.rules


def test_get_missing_analytics_rule(fake_analytics_rules: AnalyticsRules) -> None:
    """Test that the AnalyticsRules object can get a missing analytics_rule."""
    analytics_rule = fake_analytics_rules["company_analytics_rule"]

    assert analytics_rule.rule_id == "company_analytics_rule"
    assert_match_object(analytics_rule.api_call, fake_analytics_rules.api_call)
    assert_object_lists_match(
        analytics_rule.api_call.node_manager.nodes,
        fake_analytics_rules.api_call.node_manager.nodes,
    )
    assert_match_object(
        analytics_rule.api_call.config.nearest_node,
        fake_analytics_rules.api_call.config.nearest_node,
    )
    assert (
        analytics_rule._endpoint_path  # noqa: WPS437
        == "/analytics/rules/company_analytics_rule"
    )


def test_get_existing_analytics_rule(fake_analytics_rules: AnalyticsRules) -> None:
    """Test that the AnalyticsRules object can get an existing analytics_rule."""
    analytics_rule = fake_analytics_rules["company_analytics_rule"]
    fetched_analytics_rule = fake_analytics_rules["company_analytics_rule"]

    assert len(fake_analytics_rules.rules) == 1

    assert analytics_rule is fetched_analytics_rule


def test_retrieve(fake_analytics_rules: AnalyticsRules) -> None:
    """Test that the AnalyticsRules object can retrieve analytics_rules."""
    json_response: RulesRetrieveSchema = {
        "rules": [
            {
                "name": "company_analytics_rule",
                "params": {
                    "destination": {
                        "collection": "companies_queries",
                    },
                    "source": {"collections": ["companies"]},
                },
                "type": "nohits_queries",
            },
        ],
    }

    with requests_mock.Mocker() as mock:
        mock.get(
            "http://nearest:8108/analytics/rules",
            json=json_response,
        )

        response = fake_analytics_rules.retrieve()

        assert len(response) == 1
        assert response["rules"][0] == json_response.get("rules")[0]
        assert response == json_response


def test_create(fake_analytics_rules: AnalyticsRules) -> None:
    """Test that the AnalyticsRules object can create a analytics_rule."""
    json_response: RuleCreateSchemaForQueries = {
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
        mock.post(
            "http://nearest:8108/analytics/rules",
            json=json_response,
        )

        fake_analytics_rules.create(
            rule={
                "params": {
                    "destination": {
                        "collection": "companies_queries",
                    },
                    "source": {"collections": ["companies"]},
                },
                "type": "nohits_queries",
                "name": "company_analytics_rule",
            },
        )

        assert mock.call_count == 1
        assert mock.called is True
        assert mock.last_request.method == "POST"
        assert mock.last_request.url == "http://nearest:8108/analytics/rules"
        assert mock.last_request.json() == {
            "params": {
                "destination": {
                    "collection": "companies_queries",
                },
                "source": {"collections": ["companies"]},
            },
            "type": "nohits_queries",
            "name": "company_analytics_rule",
        }


def test_actual_create(
    actual_analytics_rules: AnalyticsRules,
    delete_all: None,
    delete_all_analytics_rules: None,
    create_collection: None,
    create_query_collection: None,
) -> None:
    """Test that the AnalyticsRules object can create an analytics_rule on Typesense Server."""
    response = actual_analytics_rules.create(
        rule={
            "name": "company_analytics_rule",
            "type": "nohits_queries",
            "params": {
                "source": {
                    "collections": ["companies"],
                },
                "destination": {"collection": "companies_queries"},
            },
        },
    )

    assert response == {
        "name": "company_analytics_rule",
        "type": "nohits_queries",
        "params": {
            "source": {"collections": ["companies"]},
            "destination": {"collection": "companies_queries"},
        },
    }


def test_actual_update(
    actual_analytics_rules: AnalyticsRules,
    delete_all: None,
    delete_all_analytics_rules: None,
    create_analytics_rule: None,
) -> None:
    """Test that the AnalyticsRules object can update an analytics_rule on Typesense Server."""
    response = actual_analytics_rules.upsert(
        "company_analytics_rule",
        {
            "type": "popular_queries",
            "params": {
                "source": {
                    "collections": ["companies"],
                },
                "destination": {"collection": "companies_queries"},
            },
        },
    )

    assert response == {
        "name": "company_analytics_rule",
        "type": "popular_queries",
        "params": {
            "source": {"collections": ["companies"]},
            "destination": {"collection": "companies_queries"},
        },
    }


def test_actual_retrieve(
    actual_analytics_rules: AnalyticsRules,
    delete_all: None,
    delete_all_analytics_rules: None,
    create_analytics_rule: None,
) -> None:
    """Test that the AnalyticsRules object can retrieve the rules from Typesense Server."""
    response = actual_analytics_rules.retrieve()
    assert len(response["rules"]) == 1
    assert_match_object(
        response["rules"][0],
        {
            "name": "company_analytics_rule",
            "params": {
                "destination": {"collection": "companies_queries"},
                "limit": 1000,
                "source": {"collections": ["companies"]},
            },
            "type": "nohits_queries",
        },
    )
