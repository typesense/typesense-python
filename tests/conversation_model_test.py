"""Tests for the ConversationModel class."""

from __future__ import annotations

import pytest
import requests_mock
from dotenv import load_dotenv

from tests.utils.object_assertions import (
    assert_match_object,
    assert_object_lists_match,
    assert_to_contain_keys,
)
from typesense.api_call import ApiCall
from typesense.conversation_model import ConversationModel
from typesense.conversations_models import ConversationsModels
from typesense.types.conversations_model import (
    ConversationModelDeleteSchema,
    ConversationModelSchema,
)

load_dotenv()


def test_init(fake_api_call: ApiCall) -> None:
    """Test that the ConversationModel object is initialized correctly."""
    conversation_model = ConversationModel(
        fake_api_call,
        "conversation_model_id",
    )

    assert conversation_model.model_id == "conversation_model_id"
    assert_match_object(conversation_model.api_call, fake_api_call)
    assert_object_lists_match(conversation_model.api_call.nodes, fake_api_call.nodes)
    assert_match_object(
        conversation_model.api_call.config.nearest_node,
        fake_api_call.config.nearest_node,
    )
    assert (
        conversation_model._endpoint_path  # noqa: WPS437
        == "/conversations/models/conversation_model_id"
    )


def test_retrieve(fake_conversation_model: ConversationModel) -> None:
    """Test that the ConversationModel object can retrieve a conversation_model."""
    json_response: ConversationModelSchema = {
        "api_key": "abc",
        "id": "conversation_model_id",
        "max_bytes": 1000000,
        "model_name": "conversation_model_name",
        "system_prompt": "This is a system prompt",
    }

    with requests_mock.Mocker() as mock:
        mock.get(
            "/conversations/models/conversation_model_id",
            json=json_response,
        )

        response = fake_conversation_model.retrieve()

        assert len(mock.request_history) == 1
        assert mock.request_history[0].method == "GET"
        assert (
            mock.request_history[0].url
            == "http://nearest:8108/conversations/models/conversation_model_id"
        )
        assert response == json_response


def test_delete(fake_conversation_model: ConversationModel) -> None:
    """Test that the ConversationModel object can delete a conversation_model."""
    json_response: ConversationModelDeleteSchema = {
        "id": "conversation_model_id",
    }
    with requests_mock.Mocker() as mock:
        mock.delete(
            "/conversations/models/conversation_model_id",
            json=json_response,
        )

        response = fake_conversation_model.delete()

        assert len(mock.request_history) == 1
        assert mock.request_history[0].method == "DELETE"
        assert (
            mock.request_history[0].url
            == "http://nearest:8108/conversations/models/conversation_model_id"
        )
        assert response == json_response


@pytest.mark.open_ai
def test_actual_retrieve(
    actual_conversations_models: ConversationsModels,
    delete_all_conversations_models: None,
    create_conversations_model: str,
) -> None:
    """Test it can retrieve a conversation_model from Typesense Server."""
    response = actual_conversations_models[create_conversations_model].retrieve()

    assert_to_contain_keys(
        response,
        ["id", "model_name", "system_prompt", "max_bytes", "api_key"],
    )
    assert response.get("id") == create_conversations_model


@pytest.mark.open_ai
def test_actual_update(
    actual_conversations_models: ConversationsModels,
    delete_all_conversations_models: None,
    create_conversations_model: str,
) -> None:
    """Test that it can update a conversation_model from Typesense Server."""
    response = actual_conversations_models[create_conversations_model].update(
        {"system_prompt": "This is a new system prompt"},
    )

    assert_to_contain_keys(
        response,
        [
            "id",
            "model_name",
            "system_prompt",
            "max_bytes",
            "api_key",
            "ttl",
            "history_collection",
        ],
    )

    assert response.get("system_prompt") == "This is a new system prompt"
    assert response.get("id") == create_conversations_model


@pytest.mark.open_ai
def test_actual_delete(
    actual_conversations_models: ConversationsModels,
    delete_all_conversations_models: None,
    create_conversations_model: str,
) -> None:
    """Test that it can delete an conversation_model from Typesense Server."""
    response = actual_conversations_models[create_conversations_model].delete()

    assert_to_contain_keys(
        response,
        [
            "id",
            "model_name",
            "system_prompt",
            "max_bytes",
            "api_key",
            "ttl",
            "history_collection",
        ],
    )

    assert response.get("system_prompt") == "This is a system prompt"
    assert response.get("id") == create_conversations_model
    assert response.get("id") == create_conversations_model
