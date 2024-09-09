"""Fixtures for the conversation model tests."""

import os

import pytest
import requests
from dotenv import load_dotenv

from typesense.api_call import ApiCall
from typesense.conversation_model import ConversationModel
from typesense.conversations_models import ConversationsModels

load_dotenv()


@pytest.fixture(scope="function", name="delete_all_conversations_models")
def clear_typesense_conversations_models() -> None:
    """Remove all conversations_models from the Typesense server."""
    url = "http://localhost:8108/conversations/models"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}

    # Get the list of collections
    response = requests.get(url, headers=headers, timeout=3)
    response.raise_for_status()

    conversations_models = response.json()

    # Delete each conversation model
    for conversation_model in conversations_models:
        conversation_model_id = conversation_model.get("id")
        delete_url = f"{url}/{conversation_model_id}"
        delete_response = requests.delete(delete_url, headers=headers, timeout=3)
        delete_response.raise_for_status()


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


@pytest.fixture(scope="function", name="fake_conversations_models")
def fake_conversations_models_fixture(fake_api_call: ApiCall) -> ConversationsModels:
    """Return a Collection object with test values."""
    return ConversationsModels(fake_api_call)


@pytest.fixture(scope="function", name="fake_conversation_model")
def fake_conversation_model_fixture(fake_api_call: ApiCall) -> ConversationModel:
    """Return a ConversationModel object with test values."""
    return ConversationModel(fake_api_call, "conversation_model_id")


@pytest.fixture(scope="function", name="actual_conversations_models")
def actual_conversations_models_fixture(
    actual_api_call: ApiCall,
) -> ConversationsModels:
    """Return a ConversationsModels object using a real API."""
    return ConversationsModels(actual_api_call)


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
