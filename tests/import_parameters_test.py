"""Tests for the import parameters and the batch size of an import."""

import json
import sys

import pytest

from tests.utils.backends import Backend, RequestType, load_backend
from typesense.configuration import Configuration
from typesense.http_backend import ResponseType
from typesense.sync.api_call import ApiCall
from typesense.sync.documents import Documents
from typesense.types.document import (
    DocumentImportParameters,
    DocumentImportParametersReturnDoc,
    DocumentImportParametersReturnDocAndId,
    DocumentImportParametersReturnId,
    DocumentImportWriteParameters,
    DocumentSchema,
)

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

IMPORT_PATH: typing.Final = "/collections/books/documents/import"


@pytest.fixture(name="backend", params=["httpx", "httpx2"])
def backend_fixture(request: pytest.FixtureRequest) -> Backend:
    """Return each HTTP backend that is installed."""
    name = request.param
    assert isinstance(name, str)
    return load_backend(name)


def make_documents(
    backend: Backend,
    config: Configuration,
    requests: typing.List[RequestType],
) -> Documents[DocumentSchema]:
    """Return documents that record each request and answer each line with success."""

    def handler(request: RequestType) -> ResponseType:
        requests.append(request)
        lines = request.content.decode().split("\n")
        body = "\n".join(json.dumps({"success": True}) for _ in lines)
        return backend.Response(200, content=body.encode())

    api_call = ApiCall(config, backend.client(handler))
    return Documents[DocumentSchema](api_call, "books")


@pytest.mark.parametrize(
    "parameters_type",
    [
        DocumentImportWriteParameters,
        DocumentImportParametersReturnId,
        DocumentImportParametersReturnDoc,
        DocumentImportParametersReturnDocAndId,
    ],
)
def test_import_parameters_accept_the_server_batch_size(
    parameters_type: typing.Type[typing.Any],
) -> None:
    """Test that each import parameters type has the server's batch_size."""
    hints = typing.get_type_hints(parameters_type)

    assert hints["batch_size"] is int
    assert "batch_size" in parameters_type.__optional_keys__


def test_import_parameters_union_has_the_plain_import_parameters() -> None:
    """Test that a plain import uses the type with the server's batch_size."""
    assert DocumentImportWriteParameters in typing.get_args(DocumentImportParameters)


def test_batch_size_in_import_parameters_goes_to_the_server(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that batch_size in import_parameters is sent as a query parameter."""
    requests: typing.List[RequestType] = []
    documents = make_documents(backend, fake_config, requests)
    parameters: DocumentImportWriteParameters = {"batch_size": 42}

    documents.import_([{"id": "1"}, {"id": "2"}], parameters)

    assert len(requests) == 1
    assert requests[0].url.path == IMPORT_PATH
    assert requests[0].url.params["batch_size"] == "42"


def test_batch_size_argument_splits_the_requests_on_the_client(
    backend: Backend,
    fake_config: Configuration,
) -> None:
    """Test that the batch_size argument splits the list and is not sent."""
    requests: typing.List[RequestType] = []
    documents = make_documents(backend, fake_config, requests)

    response = documents.import_(
        [{"id": "1"}, {"id": "2"}, {"id": "3"}],
        batch_size=2,
    )

    assert len(response) == 3
    assert [len(request.content.decode().split("\n")) for request in requests] == [2, 1]
    assert all("batch_size" not in request.url.params for request in requests)
