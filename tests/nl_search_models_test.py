"""Tests for the NLSearchModels class."""

from __future__ import annotations

import os
import sys

import pytest

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

from tests.utils.object_assertions import (
    assert_match_object,
    assert_object_lists_match,
    assert_to_contain_keys,
    assert_to_contain_object,
)
from typesense.api_call import ApiCall
from typesense.nl_search_models import NLSearchModels
from typesense.types.nl_search_model import NLSearchModelSchema


def test_init(fake_api_call: ApiCall) -> None:
    """Test that the NLSearchModels object is initialized correctly."""
    nl_search_models = NLSearchModels(fake_api_call)

    assert_match_object(nl_search_models.api_call, fake_api_call)
    assert_object_lists_match(
        nl_search_models.api_call.node_manager.nodes,
        fake_api_call.node_manager.nodes,
    )
    assert_match_object(
        nl_search_models.api_call.config.nearest_node,
        fake_api_call.config.nearest_node,
    )

    assert not nl_search_models.nl_search_models


def test_get_missing_nl_search_model(
    fake_nl_search_models: NLSearchModels,
) -> None:
    """Test that the NLSearchModels object can get a missing nl_search_model."""
    nl_search_model = fake_nl_search_models["nl_search_model_id"]

    assert_match_object(
        nl_search_model.api_call,
        fake_nl_search_models.api_call,
    )
    assert_object_lists_match(
        nl_search_model.api_call.node_manager.nodes,
        fake_nl_search_models.api_call.node_manager.nodes,
    )
    assert_match_object(
        nl_search_model.api_call.config.nearest_node,
        fake_nl_search_models.api_call.config.nearest_node,
    )
    assert (
        nl_search_model._endpoint_path  # noqa: WPS437
        == "/nl_search_models/nl_search_model_id"
    )


def test_get_existing_nl_search_model(
    fake_nl_search_models: NLSearchModels,
) -> None:
    """Test that the NLSearchModels object can get an existing nl_search_model."""
    nl_search_model = fake_nl_search_models["nl_search_model_id"]
    fetched_nl_search_model = fake_nl_search_models["nl_search_model_id"]

    assert len(fake_nl_search_models.nl_search_models) == 1

    assert nl_search_model is fetched_nl_search_model


@pytest.mark.open_ai
def test_actual_create(
    actual_nl_search_models: NLSearchModels,
) -> None:
    """Test that it can create an NL search model on Typesense Server."""
    response = actual_nl_search_models.create(
        {
            "api_key": os.environ.get("OPEN_AI_KEY", "test-api-key"),
            "max_bytes": 16384,
            "model_name": "openai/gpt-3.5-turbo",
            "system_prompt": "This is meant for testing purposes",
        },
    )

    assert_to_contain_keys(
        response,
        ["id", "api_key", "max_bytes", "model_name", "system_prompt"],
    )


@pytest.mark.open_ai
def test_actual_retrieve(
    actual_nl_search_models: NLSearchModels,
    delete_all_nl_search_models: None,
    create_nl_search_model: str,
) -> None:
    """Test that it can retrieve NL search models from Typesense Server."""
    response = actual_nl_search_models.retrieve()
    assert len(response) == 1
    assert_to_contain_object(
        response[0],
        {
            "id": create_nl_search_model,
        },
    )
    assert_to_contain_keys(
        response[0],
        ["id", "api_key", "max_bytes", "model_name", "system_prompt"],
    )
