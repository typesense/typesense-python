"""Tests for Analytics events endpoints (client.analytics.events)."""

from __future__ import annotations

import pytest
import requests_mock

from tests.utils.version import is_v30_or_above
from typesense.client import Client
from typesense.types.analytics import AnalyticsEvent

pytestmark = pytest.mark.skipif(
    not is_v30_or_above(
        Client(
            {
                "api_key": "xyz",
                "nodes": [{"host": "localhost", "port": 8108, "protocol": "http"}],
            }
        )
    ),
    reason="Run analytics events tests only on v30+",
)


def test_actual_create_event(
    actual_client: Client,
    delete_all: None,
    create_collection: None,
    delete_all_analytics_rules: None,
) -> None:
    actual_client.analytics.rules.create(
        {
            "name": "company_analytics_rule",
            "type": "log",
            "collection": "companies",
            "event_type": "click",
            "params": {},
        }
    )
    event: AnalyticsEvent = {
        "name": "company_analytics_rule",
        "event_type": "query",
        "data": {
            "user_id": "user-1",
            "doc_id": "apple",
        },
    }
    resp = actual_client.analytics.events.create(event)
    assert resp["ok"] is True
    actual_client.analytics.rules["company_analytics_rule"].delete()


def test_create_event(fake_client: Client) -> None:
    event: AnalyticsEvent = {
        "name": "company_analytics_rule",
        "event_type": "query",
        "data": {"user_id": "user-1", "q": "apple"},
    }
    with requests_mock.Mocker() as mock:
        mock.post("http://nearest:8108/analytics/events", json={"ok": True})
        resp = fake_client.analytics.events.create(event)
        assert resp["ok"] is True


def test_status(actual_client: Client, delete_all: None) -> None:
    status = actual_client.analytics.events.status()
    assert isinstance(status, dict)


def test_retrieve_events(
    actual_client: Client, delete_all: None, delete_all_analytics_rules: None
) -> None:
    actual_client.collections.create(
        {
            "name": "companies",
            "fields": [
                {"name": "user_id", "type": "string"},
            ],
        }
    )

    actual_client.analytics.rules.create(
        {
            "name": "company_analytics_rule",
            "type": "log",
            "collection": "companies",
            "event_type": "click",
            "params": {},
        }
    )
    event: AnalyticsEvent = {
        "name": "company_analytics_rule",
        "event_type": "query",
        "data": {
            "user_id": "user-1",
            "doc_id": "apple",
        },
    }
    resp = actual_client.analytics.events.create(event)
    assert resp["ok"] is True
    result = actual_client.analytics.events.retrieve(
        user_id="user-1",
        name="company_analytics_rule",
        n=10,
    )
    assert "events" in result


def test_acutal_retrieve_events(
    actual_client: Client,
    delete_all: None,
    create_collection: None,
    delete_all_analytics_rules: None,
) -> None:
    actual_client.analytics.rules.create(
        {
            "name": "company_analytics_rule",
            "type": "log",
            "collection": "companies",
            "event_type": "click",
            "params": {},
        }
    )
    event: AnalyticsEvent = {
        "name": "company_analytics_rule",
        "event_type": "query",
        "data": {
            "user_id": "user-1",
            "doc_id": "apple",
        },
    }
    resp = actual_client.analytics.events.create(event)
    assert resp["ok"] is True
    result = actual_client.analytics.events.retrieve(
        user_id="user-1", name="company_analytics_rule", n=10
    )
    assert "events" in result


def test_acutal_flush(actual_client: Client, delete_all: None) -> None:
    resp = actual_client.analytics.events.flush()
    assert resp["ok"] in [True, False]


def test_flush(fake_client: Client) -> None:
    with requests_mock.Mocker() as mock:
        mock.post("http://nearest:8108/analytics/flush", json={"ok": True})
        resp = fake_client.analytics.events.flush()
        assert resp["ok"] is True
