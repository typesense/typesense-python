"""Tests for the AnalyticsV1 class."""

import pytest
from tests.utils.version import is_v30_or_above
from typesense.client import Client
from tests.utils.object_assertions import assert_match_object, assert_object_lists_match
from typesense.analytics_v1 import AnalyticsV1
from typesense.api_call import ApiCall


@pytest.mark.skipif(
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
    """Test that the AnalyticsV1 object is initialized correctly."""
    analytics = AnalyticsV1(fake_api_call)

    assert_match_object(analytics.rules.api_call, fake_api_call)
    assert_object_lists_match(
        analytics.rules.api_call.node_manager.nodes,
        fake_api_call.node_manager.nodes,
    )
    assert_match_object(
        analytics.rules.api_call.config.nearest_node,
        fake_api_call.config.nearest_node,
    )

    assert not analytics.rules.rules
