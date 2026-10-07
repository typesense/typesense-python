"""Tests for the AnalyticsRulesV1 class."""

import pytest

from tests.utils.object_assertions import assert_match_object, assert_object_lists_match
from tests.utils.version import is_v30_or_above
from typesense.sync.client import Client
from typesense.sync.analytics_rules_v1 import AnalyticsRulesV1
from typesense.sync.api_call import ApiCall
from typesense.async_.api_call import AsyncApiCall
from typesense.async_.analytics_rules_v1 import AsyncAnalyticsRulesV1


pytestmark = pytest.mark.skipif(
    is_v30_or_above(
        Client(
            {
                "api_key": "xyz",
                "nodes": [{"host": "localhost", "port": 8108, "protocol": "http"}],
            }
        )
    ),
    reason="Skip AnalyticsV1 tests on v30+",
)


def test_init(fake_api_call: ApiCall) -> None:
    """Test that the AnalyticsRulesV1 object is initialized correctly."""
    analytics_rules = AnalyticsRulesV1(fake_api_call)

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


def test_get_missing_analytics_rule(fake_analytics_rules: AnalyticsRulesV1) -> None:
    """Test that the AnalyticsRulesV1 object can get a missing analytics_rule."""
    analytics_rule = fake_analytics_rules["company_analytics_rule"]

    assert analytics_rule.rule_name == "company_analytics_rule"
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


def test_get_existing_analytics_rule(fake_analytics_rules: AnalyticsRulesV1) -> None:
    """Test that the AnalyticsRulesV1 object can get an existing analytics_rule."""
    analytics_rule = fake_analytics_rules["company_analytics_rule"]
    fetched_analytics_rule = fake_analytics_rules["company_analytics_rule"]

    assert len(fake_analytics_rules.rules) == 1

    assert analytics_rule is fetched_analytics_rule


def test_actual_create(
    actual_analytics_rules: AnalyticsRulesV1,
    delete_all: None,
    delete_all_analytics_rules_v1: None,
    create_collection: None,
    create_query_collection: None,
) -> None:
    """Test that the AnalyticsRulesV1 object can create an analytics_rule on Typesense Server."""
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
    actual_analytics_rules: AnalyticsRulesV1,
    delete_all: None,
    delete_all_analytics_rules_v1: None,
    create_analytics_rule_v1: None,
) -> None:
    """Test that the AnalyticsRulesV1 object can update an analytics_rule on Typesense Server."""
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
    actual_analytics_rules: AnalyticsRulesV1,
    delete_all: None,
    delete_all_analytics_rules_v1: None,
    create_analytics_rule_v1: None,
) -> None:
    """Test that the AnalyticsRulesV1 object can retrieve the rules from Typesense Server."""
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


def test_init_async(fake_async_api_call: AsyncApiCall) -> None:
    """Test that the AsyncAnalyticsRulesV1 object is initialized correctly."""
    analytics_rules = AsyncAnalyticsRulesV1(fake_async_api_call)

    assert_match_object(analytics_rules.api_call, fake_async_api_call)
    assert_object_lists_match(
        analytics_rules.api_call.node_manager.nodes,
        fake_async_api_call.node_manager.nodes,
    )
    assert_match_object(
        analytics_rules.api_call.config.nearest_node,
        fake_async_api_call.config.nearest_node,
    )

    assert not analytics_rules.rules


def test_get_missing_analytics_rule_async(
    fake_async_analytics_rules_v1: AsyncAnalyticsRulesV1,
) -> None:
    """Test that the AsyncAnalyticsRulesV1 object can get a missing analytics_rule."""

    analytics_rule = fake_async_analytics_rules_v1["company_analytics_rule"]

    assert analytics_rule.rule_id == "company_analytics_rule"
    assert_match_object(analytics_rule.api_call, fake_async_analytics_rules_v1.api_call)
    assert_object_lists_match(
        analytics_rule.api_call.node_manager.nodes,
        fake_async_analytics_rules_v1.api_call.node_manager.nodes,
    )
    assert_match_object(
        analytics_rule.api_call.config.nearest_node,
        fake_async_analytics_rules_v1.api_call.config.nearest_node,
    )
    assert (
        analytics_rule._endpoint_path  # noqa: WPS437
        == "/analytics/rules/company_analytics_rule"
    )


def test_get_existing_analytics_rule_async(
    fake_async_analytics_rules_v1: AsyncAnalyticsRulesV1,
) -> None:
    """Test that the AsyncAnalyticsRulesV1 object can get an existing analytics_rule."""
    analytics_rule = fake_async_analytics_rules_v1["company_analytics_rule"]
    fetched_analytics_rule = fake_async_analytics_rules_v1["company_analytics_rule"]

    assert len(fake_async_analytics_rules_v1.rules) == 1

    assert analytics_rule is fetched_analytics_rule


async def test_actual_create_async(
    actual_async_analytics_rules_v1: AsyncAnalyticsRulesV1,
    delete_all: None,
    delete_all_analytics_rules_v1: None,
    create_collection: None,
    create_query_collection: None,
) -> None:
    """Test that the AsyncAnalyticsRulesV1 object can create an analytics_rule on Typesense Server."""
    response = await actual_async_analytics_rules_v1.create(
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


async def test_actual_update_async(
    actual_async_analytics_rules_v1: AsyncAnalyticsRulesV1,
    delete_all: None,
    delete_all_analytics_rules_v1: None,
    create_analytics_rule_v1: None,
) -> None:
    """Test that the AsyncAnalyticsRulesV1 object can update an analytics_rule on Typesense Server."""
    response = await actual_async_analytics_rules_v1.upsert(
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


async def test_actual_retrieve_async(
    actual_async_analytics_rules_v1: AsyncAnalyticsRulesV1,
    delete_all: None,
    delete_all_analytics_rules_v1: None,
    create_analytics_rule_v1: None,
) -> None:
    """Test that the AsyncAnalyticsRulesV1 object can retrieve the rules from Typesense Server."""
    response = await actual_async_analytics_rules_v1.retrieve()
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
