"""Tests for the Client class."""

import logging

from tests.fixtures.document_fixtures import Companies
from tests.utils.object_assertions import assert_match_object, assert_object_lists_match
from typesense.client import Client
from typesense.configuration import ConfigDict
import typesense.logger as typesense_logger


def test_client_init(fake_config_dict: ConfigDict) -> None:
    """Test the Client class __init__ method."""
    fake_client = Client(fake_config_dict)
    assert fake_client.config == fake_client.api_call.config

    assert_match_object(fake_client.api_call.config, fake_client.config)
    assert_object_lists_match(
        fake_client.api_call.node_manager.nodes, fake_client.config.nodes
    )
    assert_match_object(
        fake_client.api_call.config.nearest_node,
        fake_client.config.nearest_node,
    )

    assert fake_client.collections
    assert fake_client.collections.collections is not None
    assert fake_client.multi_search
    assert fake_client.keys
    assert fake_client.keys.keys is not None
    assert fake_client.aliases
    assert fake_client.aliases.aliases is not None
    assert fake_client._analyticsV1 is None
    assert fake_client.operations
    assert fake_client.debug


def test_get_collection(fake_client: Client) -> None:
    """Test the Client class get_collection method."""
    collection = fake_client.typed_collection(model=Companies, name="companies")

    assert collection
    assert collection.name == "companies"
    assert collection.documents.documents is not None


def test_get_collection_no_name(fake_client: Client) -> None:
    """Test the Client class get_collection method."""
    collection = fake_client.typed_collection(model=Companies)

    assert collection
    assert collection.name == "companies"
    assert collection.documents.documents is not None


def test_retrieve_collection_actual(
    actual_client: Client,
    delete_all: None,
    create_collection: None,
) -> None:
    """Test that the client can retrieve an actual collection."""
    collection = actual_client.typed_collection(model=Companies, name="companies")

    assert collection is not None


def test_retrieve_collection_actual_no_name(
    actual_client: Client,
    delete_all: None,
    create_collection: None,
) -> None:
    """Test that the client can retrieve an actual collection."""
    collection = actual_client.typed_collection(model=Companies)

    assert collection is not None


def test_analytics_v1_deprecation_not_logged_on_init(
    fake_config_dict: ConfigDict,
    caplog,
) -> None:
    """Test that analytics v1 deprecation is not logged on client init."""
    typesense_logger._deprecation_warnings.clear()
    caplog.set_level(logging.WARNING, logger="typesense")

    Client(fake_config_dict)

    assert "Deprecation warning:" not in caplog.text


def test_analytics_v1_deprecation_logged_once(
    fake_config_dict: ConfigDict,
    caplog,
) -> None:
    """Test that analytics v1 deprecation is logged once when used."""
    typesense_logger._deprecation_warnings.clear()
    caplog.set_level(logging.WARNING, logger="typesense")

    client = Client(fake_config_dict)
    _ = client.analyticsV1
    _ = client.analyticsV1

    message = (
        "Deprecation warning: AnalyticsRulesV1 is deprecated on v30+. "
        "Use client.analytics instead."
    )
    assert caplog.text.count(message) == 1
