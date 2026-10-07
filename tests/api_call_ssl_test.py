"""Regression tests for TLS configuration in both HTTP clients."""

import ssl
from pathlib import Path

import certifi
import pytest
from pytest_mock import MockerFixture

from typesense.async_.api_call import AsyncApiCall
from typesense.configuration import Configuration
from typesense.sync.api_call import ApiCall


@pytest.fixture(params=[ApiCall, AsyncApiCall])
def api_call_class(request):
    """Exercise both the async source and the generated sync client."""
    return request.param


def pool_ssl_context(api_call) -> ssl.SSLContext:
    """Return the SSL context of the client's connection pool.

    This reads private httpx 0.28 attributes and may need updating on upgrades.
    """
    return api_call._client._transport._pool._ssl_context


async def close_api_call(api_call):
    if isinstance(api_call, AsyncApiCall):
        await api_call.aclose()
    else:
        api_call.close()


@pytest.mark.parametrize("verify", [True, False])
async def test_verification_mode(fake_config, api_call_class, verify):
    """The effective TLS context must honor explicit verification settings."""
    fake_config.verify = verify
    api_call = api_call_class(fake_config)
    try:
        ssl_context = pool_ssl_context(api_call)
        assert ssl_context.verify_mode == (
            ssl.CERT_REQUIRED if verify else ssl.CERT_NONE
        )
        assert ssl_context.check_hostname is verify
    finally:
        await close_api_call(api_call)


async def test_ssl_context(fake_config, api_call_class):
    """A configured SSL context must be used as is."""
    context = ssl.create_default_context()
    fake_config.verify = context
    api_call = api_call_class(fake_config)
    try:
        assert pool_ssl_context(api_call) is context
    finally:
        await close_api_call(api_call)


async def test_custom_ca_bundle(
    fake_config: Configuration,
    api_call_class,
    tmp_path: Path,
    mocker: MockerFixture,
):
    """A configured CA bundle must reach the real SSL context builder."""
    ca_bundle = tmp_path / "custom-ca.pem"
    ca_bundle.write_bytes(Path(certifi.where()).read_bytes())
    fake_config.verify = str(ca_bundle)
    create_context = mocker.spy(ssl, "create_default_context")

    api_call = api_call_class(fake_config)
    try:
        create_context.assert_any_call(cafile=str(ca_bundle))
    finally:
        await close_api_call(api_call)


async def test_missing_ca_bundle(fake_config, api_call_class, tmp_path):
    """An invalid CA path must fail instead of silently using default trust roots."""
    fake_config.verify = str(tmp_path / "missing-ca.pem")
    with pytest.raises(FileNotFoundError):
        api_call_class(fake_config)
