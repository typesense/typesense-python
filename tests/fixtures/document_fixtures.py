"""Fixtures for creating documents in the Typesense server."""

import sys

import pytest
import requests
from faker import Faker
from faker.providers import company

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

from typesense.api_call import ApiCall
from typesense.document import Document
from typesense.documents import Documents

fake = Faker()
fake.add_provider(company)


@pytest.fixture(scope="function", name="create_document")
def create_document_fixture() -> None:
    """Create a document in the Typesense server."""
    url = "http://localhost:8108/collections/companies/documents"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}
    document_data = {
        "id": "0",
        "company_name": "Company",
        "num_employees": 10,
    }

    response = requests.post(url, headers=headers, json=document_data, timeout=3)
    response.raise_for_status()


@pytest.fixture(scope="function", name="actual_documents")
def actual_documents_fixture(actual_api_call: ApiCall) -> Documents:
    """Return a Documents object using a real API."""
    return Documents(actual_api_call, "companies")


@pytest.fixture(scope="function", name="fake_documents")
def fake_documents_fixture(fake_api_call: ApiCall) -> Documents:
    """Return a Documents object with test values."""
    return Documents(fake_api_call, "companies")


@pytest.fixture(scope="function", name="fake_document")
def fake_document_fixture(fake_api_call: ApiCall) -> Document:
    """Return a Document object with test values."""
    return Document(fake_api_call, "companies", "0")


class Companies(typing.TypedDict):
    """Company data type."""

    id: str
    company_name: str
    num_employees: int


@pytest.fixture(scope="function", name="generate_companies")
def generate_companies_fixture() -> typing.List[Companies]:
    """Generate a list of companies using fake data."""
    companies: typing.List[Companies] = []
    for company_index in range(50):
        companies.append(
            {
                "id": str(company_index),
                "company_name": fake.company(),
                "num_employees": fake.random_int(1, 1000),
            },
        )

    return companies
