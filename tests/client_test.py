"""Tests for the Client class."""

import httpx

from tests.fixtures.document_fixtures import Companies
from tests.utils.object_assertions import assert_match_object, assert_object_lists_match
from typesense.async_.client import AsyncClient
from typesense.sync.client import Client
from typesense.configuration import ConfigDict


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
    assert fake_client.analyticsV1
    assert fake_client.analyticsV1.rules
    assert fake_client.analyticsV1.rules.rules is not None
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


def test_client_close(fake_config_dict: ConfigDict) -> None:
    """Test that Client.close closes an owned HTTP client."""
    client = Client(fake_config_dict)
    assert client.api_call._client.is_closed is False
    client.close()
    assert client.api_call._client.is_closed is True


def test_client_context_manager(fake_config_dict: ConfigDict) -> None:
    """Test that Client closes its HTTP client when used as a context manager."""
    with Client(fake_config_dict) as client:
        assert client.api_call._client.is_closed is False
    assert client.api_call._client.is_closed is True


def test_client_does_not_close_external_http_client(
    fake_config_dict: ConfigDict,
) -> None:
    """Test that Client.close does not close a caller-supplied http_client."""
    external_client = httpx.Client()
    try:
        with Client(fake_config_dict, http_client=external_client) as client:
            assert client.api_call._client is external_client
        assert external_client.is_closed is False
    finally:
        external_client.close()


async def test_async_client_aclose(fake_config_dict: ConfigDict) -> None:
    """Test that AsyncClient.aclose closes an owned HTTP client."""
    client = AsyncClient(fake_config_dict)
    assert client.api_call._client.is_closed is False
    await client.aclose()
    assert client.api_call._client.is_closed is True


async def test_async_client_context_manager(fake_config_dict: ConfigDict) -> None:
    """Test that AsyncClient closes its HTTP client when used as an async context manager."""
    async with AsyncClient(fake_config_dict) as client:
        assert client.api_call._client.is_closed is False
    assert client.api_call._client.is_closed is True


async def test_async_client_does_not_close_external_http_client(
    fake_config_dict: ConfigDict,
) -> None:
    """Test that AsyncClient.aclose does not close a caller-supplied http_client."""
    external_client = httpx.AsyncClient()
    try:
        async with AsyncClient(fake_config_dict, http_client=external_client) as client:
            assert client.api_call._client is external_client
        assert external_client.is_closed is False
    finally:
        await external_client.aclose()
