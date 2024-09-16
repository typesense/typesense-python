"""Fixtures for the client tests."""

import pytest

from typesense.client import Client
from typesense.configuration import ConfigDict


@pytest.fixture(scope="function", name="fake_client")
def fake_client_fixture(
    fake_config_dict: ConfigDict,
) -> Client:
    """Return a client object with test values."""
    return Client(fake_config_dict)


@pytest.fixture(scope="function", name="actual_client")
def actual_client_fixture(actual_config_dict: ConfigDict) -> Client:
    """Return a client object using a real API."""
    return Client(actual_config_dict)
