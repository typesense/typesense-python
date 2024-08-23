"""Tests for the Analytics class."""

from tests.utils.object_assertions import assert_match_object, assert_object_lists_match
from typesense.analytics import Analytics
from typesense.api_call import ApiCall


def test_init(fake_api_call: ApiCall) -> None:
    """Test that the Analytics object is initialized correctly."""
    analytics = Analytics(fake_api_call)

    assert_match_object(analytics.rules.api_call, fake_api_call)
    assert_object_lists_match(analytics.rules.api_call.nodes, fake_api_call.nodes)
    assert_match_object(
        analytics.rules.api_call.config.nearest_node,
        fake_api_call.config.nearest_node,
    )

    assert not analytics.rules.rules
