"""Pytest configuration file."""

import pytest
import requests
from faker import Faker
from faker.providers import company

from typesense.alias import Alias
from typesense.aliases import Aliases
from typesense.analytics_rule import AnalyticsRule
from typesense.analytics_rules import AnalyticsRules
from typesense.api_call import ApiCall
from typesense.collection import Collection
from typesense.collections import Collections
from typesense.configuration import Configuration
from typesense.conversation_model import ConversationModel
from typesense.conversations_models import ConversationsModels
from typesense.document import Document
from typesense.documents import Documents
from typesense.key import Key
from typesense.keys import Keys
from typesense.multi_search import MultiSearch
from typesense.operations import Operations
from typesense.override import Override
from typesense.overrides import Overrides
from typesense.stopwords import Stopwords
from typesense.stopwords_set import StopwordsSet
from typesense.synonym import Synonym
from typesense.synonyms import Synonyms

pytest.register_assert_rewrite("utils.object_assertions")

fake = Faker()
fake.add_provider(company)


@pytest.fixture(scope="function", name="delete_all")
def clear_typesense_collections() -> None:
    """Remove all collections from the Typesense server."""
    url = "http://localhost:8108/collections"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}

    # Get the list of collections
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    collections = response.json()

    # Delete each collection
    for collection in collections:
        collection_name = collection["name"]
        delete_url = f"{url}/{collection_name}"
        delete_response = requests.delete(delete_url, headers=headers)
        delete_response.raise_for_status()


@pytest.fixture(scope="function", name="create_collection")
def create_collection_fixture() -> None:
    """Create a collection in the Typesense server."""
    url = "http://localhost:8108/collections"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}
    data = {
        "name": "companies",
        "fields": [
            {
                "name": "company_name",
                "type": "string",
            },
            {
                "name": "num_employees",
                "type": "int32",
            },
        ],
        "default_sorting_field": "num_employees",
    }

    response = requests.post(url, headers=headers, json=data)
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


@pytest.fixture(scope="function", name="create_conversation_history_collection")
def create_conversation_history_collection_fixture() -> None:
    """Create a collection for conversation history in the Typesense server."""
    url = "http://localhost:8108/collections"
    delete_url = "http://localhost:8108/collections/conversation_store"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}
    collection_data = {
        "name": "conversation_store",
        "fields": [
            {"name": "conversation_id", "type": "string"},
            {"name": "model_id", "type": "string"},
            {"name": "timestamp", "type": "int32"},
            {"name": "role", "type": "string", "index": False},
            {"name": "message", "type": "string", "index": False},
        ],
    }

    delete_response = requests.delete(delete_url, headers=headers, timeout=3)
    if delete_response.status_code not in {200, 404}:
        delete_response.raise_for_status()
    response = requests.post(url, headers=headers, json=collection_data, timeout=3)
    response.raise_for_status()


@pytest.fixture(scope="function", name="create_conversations_model")
def create_conversations_model_fixture(
    create_conversation_history_collection: None,
) -> str:
    """Create a conversations model in the Typesense server."""
    url = "http://localhost:8108/conversations/models"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}
    conversations_model_data = {
        "api_key": os.environ["OPEN_AI_KEY"],
        "max_bytes": 16384,
        "model_name": "openai/gpt-3.5-turbo",
        "history_collection": "conversation_store",
        "system_prompt": "This is a system prompt",
    }

    response = requests.post(
        url,
        headers=headers,
        json=conversations_model_data,
        timeout=3,
    )

    response.raise_for_status()

    conversation_model_id: str = response.json()["id"]
    return conversation_model_id


@pytest.fixture(scope="function", name="create_stopword")
def create_stopword_fixture() -> None:
    """Create a stopword set in the Typesense server."""
    url = "http://localhost:8108/stopwords/company_stopwords"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}
    stopword_data = {
        "stopwords": ["and", "is", "the"],
    }

    response = requests.put(url, headers=headers, json=stopword_data, timeout=3)
    response.raise_for_status()


@pytest.fixture(scope="function", name="create_key_id")
def create_key_fixture() -> int:
    """Create a key set in the Typesense server."""
    url = "http://localhost:8108/keys"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}
    api_key_data = {
        "actions": ["documents:search"],
        "collections": ["companies"],
        "description": "Search-only key",
    }

    response = requests.post(url, headers=headers, json=api_key_data, timeout=3)
    response.raise_for_status()
    key_id: int = response.json()["id"]
    return key_id


@pytest.fixture(scope="function", name="delete_all_aliases")
def clear_typesense_aliases() -> None:
    """Remove all aliases from the Typesense server."""
    url = "http://localhost:8108/aliases"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}

    # Get the list of collections
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    aliases = response.json()

    # Delete each alias
    for alias in aliases["aliases"]:
        alias_name = alias.get("name")
        delete_url = f"{url}/{alias_name}"
        delete_response = requests.delete(delete_url, headers=headers)
@pytest.fixture(scope="function", name="delete_all_conversations_models")
def clear_typesense_conversations_models() -> None:
    """Remove all conversations_models from the Typesense server."""
    url = "http://localhost:8108/conversations/models"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}

    # Get the list of collections
    response = requests.get(url, headers=headers, timeout=3)
    response.raise_for_status()

    conversations_models = response.json()

    # Delete each alias
    for conversation_model in conversations_models:
        conversation_model_id = conversation_model.get("id")
        delete_url = f"{url}/{conversation_model_id}"
        delete_response = requests.delete(delete_url, headers=headers, timeout=3)
        delete_response.raise_for_status()


@pytest.fixture(scope="function", name="delete_all_stopwords")
def clear_typesense_stopwords() -> None:
    """Remove all stopwords from the Typesense server."""
    url = "http://localhost:8108/stopwords"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}

    # Get the list of collections
    response = requests.get(url, headers=headers, timeout=3)
    response.raise_for_status()
    stopwords = response.json()

    # Delete each stopword
    for stopword_set in stopwords["stopwords"]:
        stopword_id = stopword_set.get("id")
        delete_url = f"{url}/{stopword_id}"
        delete_response = requests.delete(delete_url, headers=headers, timeout=3)
        delete_response.raise_for_status()


@pytest.fixture(scope="function", name="delete_all_keys")
def clear_typesense_keys() -> None:
    """Remove all keys from the Typesense server."""
    url = "http://localhost:8108/keys"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}

    # Get the list of collections
    response = requests.get(url, headers=headers, timeout=3)
    response.raise_for_status()

    keys = response.json()

    # Delete each key
    for key in keys["keys"]:
        key_name = key.get("id")
        delete_url = f"{url}/{key_name}"
        delete_response = requests.delete(delete_url, headers=headers, timeout=3)
        delete_response.raise_for_status()


@pytest.fixture(scope="function", name="delete_all_analytics_rules")
def clear_typesense_analytics_rules() -> None:
    """Remove all analytics_rules from the Typesense server."""
    url = "http://localhost:8108/analytics/rules"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}

    # Get the list of collections
    response = requests.get(url, headers=headers, timeout=3)
    response.raise_for_status()
    analytics_rules = response.json()

    # Delete each analytics_rule
    for analytics_rule_set in analytics_rules["rules"]:
        analytics_rule_id = analytics_rule_set.get("name")
        delete_url = f"{url}/{analytics_rule_id}"
        delete_response = requests.delete(delete_url, headers=headers, timeout=3)
        delete_response.raise_for_status()


@pytest.fixture(scope="function", name="create_another_collection")
def create_another_collection_fixture() -> None:
    """Create a collection in the Typesense server."""
    url = "http://localhost:8108/collections"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}
    data = {
        "name": "companies_2",
        "fields": [
            {
                "name": "company_name",
                "type": "string",
            },
            {
                "name": "num_employees",
                "type": "int32",
            },
        ],
        "default_sorting_field": "num_employees",
    }

    response = requests.post(url, headers=headers, json=data)

@pytest.fixture(scope="function", name="create_query_collection")
def create_query_collection_fixture() -> None:
    """Create a collection in the Typesense server."""
    url = "http://localhost:8108/collections"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}
    query_collection_data = {
        "name": "companies_queries",
        "fields": [
            {
                "name": "q",
                "type": "string",
            },
            {
                "name": "count",
                "type": "int32",
            },
        ],
    }

    response = requests.post(
        url,
        headers=headers,
        json=query_collection_data,
        timeout=3,
    )
    response.raise_for_status()


@pytest.fixture(scope="function", name="create_analytics_rule")
def create_analytics_rule_fixture(
    create_collection: None,
    create_query_collection: None,
) -> None:
    """Create a collection in the Typesense server."""
    url = "http://localhost:8108/analytics/rules"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}
    analytics_rule_data = {
        "name": "company_analytics_rule",
        "type": "nohits_queries",
        "params": {
            "source": {
                "collections": ["companies"],
            },
            "destination": {"collection": "companies_queries"},
        },
    }

    response = requests.post(url, headers=headers, json=analytics_rule_data, timeout=3)
    response.raise_for_status()


@pytest.fixture(scope="function", name="create_override")
def create_override_fixture(create_collection: None) -> None:
    url = "http://localhost:8108/collections/companies/overrides/company_override"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}
    data = {
        "rule": {"match": "exact", "query": "companies"},
        "filter_by": "num_employees>10",
    }

    response = requests.put(url, headers=headers, json=data)
    response.raise_for_status()


@pytest.fixture(scope="function", name="create_synonym")
def create_synonym_fixture(create_collection: None) -> None:
    url = "http://localhost:8108/collections/companies/synonyms/company_synonym"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}
    data = {
        "synonyms": ["companies", "corporations", "firms"],
    }

    response = requests.put(url, headers=headers, json=data)
    response.raise_for_status()


@pytest.fixture(scope="function", name="create_alias")
def create_alias_fixture(create_collection: None) -> None:
    url = "http://localhost:8108/aliases/company_alias"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}
    data = {
        "collection_name": "companies",
    }

    response = requests.put(url, headers=headers, json=data)
    response.raise_for_status()


@pytest.fixture(scope="function", name="actual_config")
def actual_config_fixture() -> Configuration:
    return Configuration(
        config_dict={
            "api_key": "xyz",
            "nodes": [
                {
                    "host": "localhost",
                    "port": 8108,
                    "protocol": "http",
                }
            ],
        }
    )


@pytest.fixture(scope="function", name="actual_api_call")
def actual_api_call_fixture(actual_config: Configuration) -> ApiCall:
    return ApiCall(actual_config)


@pytest.fixture(scope="function", name="actual_collections")
def actual_collections_fixture(actual_api_call: ApiCall) -> Collections:
    return Collections(actual_api_call)


@pytest.fixture(scope="function", name="actual_documents")
def actual_documents_fixture(actual_api_call: ApiCall) -> Documents:
    """Return a Documents object using a real API."""
    return Documents(actual_api_call, "companies")


@pytest.fixture(scope="function", name="actual_multi_search")
def actual_multi_search_fixture(actual_api_call: ApiCall) -> MultiSearch:
    """Return a MultiSearch object using a real API."""
    return MultiSearch(actual_api_call)


@pytest.fixture(scope="function", name="actual_overrides")
def actual_overrides_fixture(actual_api_call: ApiCall) -> Overrides:
    return Overrides(actual_api_call, "companies")


@pytest.fixture(scope="function", name="actual_conversations_models")
def actual_conversations_models_fixture(
    actual_api_call: ApiCall,
) -> ConversationsModels:
    """Return a ConversationsModels object using a real API."""
    return ConversationsModels(actual_api_call)


@pytest.fixture(scope="function", name="actual_synonyms")
def actual_synonyms_fixture(actual_api_call: ApiCall) -> Synonyms:
    return Synonyms(actual_api_call, "companies")


@pytest.fixture(scope="function", name="actual_aliases")
def actual_aliases_fixture(actual_api_call: ApiCall) -> Aliases:
    return Aliases(actual_api_call)


@pytest.fixture(scope="function", name="actual_stopwords")
def actual_stopwords_fixture(actual_api_call: ApiCall) -> Stopwords:
    """Return a Stopwords object using a real API."""
    return Stopwords(actual_api_call)


@pytest.fixture(scope="function", name="actual_stopwords_set")
def actual_stopwords_set_fixture(actual_api_call: ApiCall) -> StopwordsSet:
    """Return a Stopwords object using a real API."""
    return StopwordsSet(actual_api_call, "company_stopwords")


@pytest.fixture(scope="function", name="actual_operations")
def actual_operations_fixture(actual_api_call: ApiCall) -> Operations:
    """Return a Operations object using a real API."""
    return Operations(actual_api_call)


@pytest.fixture(scope="function", name="fake_config")
def fake_config_fixture() -> Configuration:
    """Return a Configuration object with test values."""
    return Configuration(
        config_dict={
            "api_key": "test-api-key",
            "nodes": [
                {
                    "host": "node0",
                    "port": 8108,
                    "protocol": "http",
                },
                {
                    "host": "node1",
                    "port": 8108,
                    "protocol": "http",
                },
                {
                    "host": "node2",
                    "port": 8108,
                    "protocol": "http",
                },
            ],
            "nearest_node": {
                "host": "nearest",
                "port": 8108,
                "protocol": "http",
            },
            "num_retries": 3,
            "healthcheck_interval_seconds": 60,
            "retry_interval_seconds": 0.001,
            "connection_timeout_seconds": 0.001,
            "verify": True,
        },
    )


@pytest.fixture(scope="function", name="fake_api_call")
def fake_api_call_fixture(
    fake_config: Configuration,
) -> ApiCall:
    """Return an ApiCall object with test values."""
    return ApiCall(fake_config)


@pytest.fixture(scope="function", name="fake_collections")
def fake_collections_fixture(fake_api_call: ApiCall) -> Collections:
    """Return a Collection object with test values."""
    return Collections(fake_api_call)


@pytest.fixture(scope="function", name="fake_analytics_rules")
def fake_analytics_rules_fixture(fake_api_call: ApiCall) -> AnalyticsRules:
    """Return a AnalyticsRule object with test values."""
    return AnalyticsRules(fake_api_call)


@pytest.fixture(scope="function", name="fake_collection")
def fake_collection_fixture(fake_api_call: ApiCall) -> Collection:
    """Return a Collection object with test values."""
    return Collection(fake_api_call, "companies")


@pytest.fixture(scope="function", name="fake_overrides")
def fake_overrides_fixture(fake_api_call: ApiCall) -> Overrides:
    """Return a Collection object with test values."""
    return Overrides(fake_api_call, "companies")


@pytest.fixture(scope="function", name="fake_conversations_models")
def fake_conversations_models_fixture(fake_api_call: ApiCall) -> ConversationsModels:
    """Return a Collection object with test values."""
    return ConversationsModels(fake_api_call)


@pytest.fixture(scope="function", name="fake_conversation_model")
def fake_conversation_model_fixture(fake_api_call: ApiCall) -> ConversationModel:
    """Return a ConversationModel object with test values."""
    return ConversationModel(fake_api_call, "conversation_model_id")


@pytest.fixture(scope="function", name="fake_override")
def fake_override_fixture(fake_api_call: ApiCall) -> Override:
    """Return a Collection object with test values."""
    return Override(fake_api_call, "companies", "company_override")


@pytest.fixture(scope="function", name="fake_synonyms")
def fake_synonyms_fixture(fake_api_call: ApiCall) -> Synonyms:
    """Return a Collection object with test values."""
    return Synonyms(fake_api_call, "companies")


@pytest.fixture(scope="function", name="fake_synonym")
def fake_synonym_fixture(fake_api_call: ApiCall) -> Synonym:
    """Return a Collection object with test values."""
    return Synonym(fake_api_call, "companies", "company_synonym")


@pytest.fixture(scope="function", name="fake_aliases")
def fake_aliases_fixture(fake_api_call: ApiCall) -> Aliases:
    """Return a Collection object with test values."""
    return Aliases(fake_api_call)


@pytest.fixture(scope="function", name="fake_alias")
def fake_alias_fixture(fake_api_call: ApiCall) -> Alias:
    """Return a Collection object with test values."""
    return Alias(fake_api_call, "company_alias")


@pytest.fixture(scope="function", name="fake_stopwords")
def fake_stopwords_fixture(fake_api_call: ApiCall) -> Stopwords:
    """Return a Stopwords object with test values."""
    return Stopwords(fake_api_call)


@pytest.fixture(scope="function", name="fake_stopwords_set")
def fake_stopwords_set_fixture(fake_api_call: ApiCall) -> StopwordsSet:
    """Return a Collection object with test values."""
    return StopwordsSet(fake_api_call, "company_stopwords")


@pytest.fixture(scope="function", name="actual_analytics_rules")
def actual_analytics_rules_fixture(actual_api_call: ApiCall) -> AnalyticsRules:
    """Return a AnalyticsRules object using a real API."""
    return AnalyticsRules(actual_api_call)


@pytest.fixture(scope="function", name="actual_keys")
def actual_keys_fixture(actual_api_call: ApiCall) -> Keys:
    """Return a Keys object using a real API."""
    return Keys(actual_api_call)


@pytest.fixture(scope="function", name="fake_analytics_rule")
def fake_analytics_rule_fixture(fake_api_call: ApiCall) -> AnalyticsRule:
    """Return a Collection object with test values."""
    return AnalyticsRule(fake_api_call, "company_analytics_rule")


@pytest.fixture(scope="function", name="fake_operations")
def fake_operations_fixture(fake_api_call: ApiCall) -> Operations:
    """Return a Collection object with test values."""
    return Operations(fake_api_call)


@pytest.fixture(scope="function", name="fake_keys")
def fake_keys_fixture(fake_api_call: ApiCall) -> Keys:
    """Return a AnalyticsRule object with test values."""
    return Keys(fake_api_call)


@pytest.fixture(scope="function", name="fake_key")
def fake_key_fixture(fake_api_call: ApiCall) -> Key:
    """Return a Key object with test values."""
    return Key(fake_api_call, 1)


@pytest.fixture(scope="function", name="fake_documents")
def fake_documents_fixture(fake_api_call: ApiCall) -> Documents:
    """Return a Documents object with test values."""
    return Documents(fake_api_call, "companies")


@pytest.fixture(scope="function", name="fake_document")
def fake_document_fixture(fake_api_call: ApiCall) -> Document:
    """Return a Document object with test values."""
    return Document(fake_api_call, "companies", "0")


class Company(typing.TypedDict):
    """Company data type."""

    id: str
    company_name: str
    num_employees: int


@pytest.fixture(scope="function", name="generate_companies")
def generate_companies_fixture() -> typing.List[Company]:
    """Generate a list of companies using fake data."""
    companies: typing.List[Company] = []
    for _ in range(50):
        companies.append(
            {
                "id": str(_),
                "company_name": fake.company(),
                "num_employees": fake.random_int(1, 1000),
            },
        )

    return companies
