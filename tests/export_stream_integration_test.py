"""Tests for streaming document exports against a Typesense server."""

import json
import sys

from typesense.async_.api_call import AsyncApiCall
from typesense.async_.documents import AsyncDocuments
from typesense.configuration import Configuration
from typesense.sync.api_call import ApiCall
from typesense.sync.documents import Documents

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

COMPANIES: typing.Final = [
    {"id": "1", "company_name": "Line separator", "num_employees": 10},
    {"id": "2", "company_name": "Next\u0085line", "num_employees": 20},
    {"id": "3", "company_name": "Ünïcode 😀", "num_employees": 30},
]
COMPANY_COUNT: typing.Final = len(COMPANIES)


def test_export_stream_matches_export(
    delete_all: None,
    create_collection: None,
    actual_api_call: ApiCall,
) -> None:
    """Test that lines and bytes match the buffered export, with and without gzip."""
    documents = Documents(actual_api_call, "companies")
    documents.import_(COMPANIES, {"action": "create"})
    exported = documents.export()

    with documents.export_stream() as stream:
        lines = list(stream)
    with documents.export_stream(compress=True) as stream:
        compressed_lines = list(stream)
    with documents.export_stream() as stream:
        body = b"".join(stream.iter_bytes())

    assert [json.loads(line) for line in lines] == COMPANIES
    assert lines == exported.split("\n")
    assert compressed_lines == lines
    assert body.decode() == exported


def test_export_stream_applies_the_parameters(
    delete_all: None,
    create_collection: None,
    actual_api_call: ApiCall,
) -> None:
    """Test a filtered export with a batch size and selected fields."""
    documents = Documents(actual_api_call, "companies")
    documents.import_(COMPANIES, {"action": "create"})

    with documents.export_stream(
        {
            "filter_by": "num_employees:>=20",
            "include_fields": "num_employees",
            "batch_size": 1,
        },
    ) as stream:
        lines = [json.loads(line) for line in stream]

    assert lines == [{"num_employees": 20}, {"num_employees": 30}]


def test_export_stream_with_no_matches_has_no_lines(
    delete_all: None,
    create_collection: None,
    actual_api_call: ApiCall,
) -> None:
    """Test that a filter matching nothing gives an empty export."""
    documents = Documents(actual_api_call, "companies")

    with documents.export_stream({"filter_by": "num_employees:>0"}) as stream:
        assert not list(stream)


def test_leaving_an_export_early_frees_the_client(
    delete_all: None,
    create_collection: None,
    actual_config: Configuration,
) -> None:
    """Test requests during and after an export at the tightest limits."""
    actual_config.max_concurrent_requests = 1
    actual_config.max_connections = 2
    api_call = ApiCall(actual_config)
    documents = Documents(api_call, "companies")
    documents.import_(COMPANIES, {"action": "create"})

    with documents.export_stream() as stream:
        assert json.loads(next(stream)) == COMPANIES[0]
        collection = api_call.get("/collections/companies", dict)
        assert collection["name"] == "companies"

    with documents.export_stream() as stream:
        assert len(list(stream)) == COMPANY_COUNT


async def test_export_stream_matches_export_async(
    delete_all: None,
    create_collection: None,
    actual_async_api_call: AsyncApiCall,
) -> None:
    """Test that lines and bytes match the buffered export, with and without gzip."""
    documents = AsyncDocuments(actual_async_api_call, "companies")
    await documents.import_(COMPANIES, {"action": "create"})
    exported = await documents.export()

    async with await documents.export_stream() as stream:
        lines = [line async for line in stream]
    async with await documents.export_stream(compress=True) as stream:
        compressed_lines = [line async for line in stream]
    async with await documents.export_stream() as stream:
        body = b"".join([chunk async for chunk in stream.aiter_bytes()])

    assert [json.loads(line) for line in lines] == COMPANIES
    assert lines == exported.split("\n")
    assert compressed_lines == lines
    assert body.decode() == exported


async def test_leaving_an_export_early_frees_the_client_async(
    delete_all: None,
    create_collection: None,
    actual_config: Configuration,
) -> None:
    """Test requests during and after an export at the tightest limits."""
    actual_config.max_concurrent_requests = 1
    actual_config.max_connections = 2
    api_call = AsyncApiCall(actual_config)
    documents = AsyncDocuments(api_call, "companies")
    await documents.import_(COMPANIES, {"action": "create"})

    async with await documents.export_stream() as stream:
        assert json.loads(await stream.__anext__()) == COMPANIES[0]
        collection = await api_call.get("/collections/companies", dict)
        assert collection["name"] == "companies"

    async with await documents.export_stream() as stream:
        assert len([line async for line in stream]) == COMPANY_COUNT
