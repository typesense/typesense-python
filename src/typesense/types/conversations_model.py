"""ConversationalModel types for Typesense Python Client."""

import sys

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing


class ConversationModelCreateSchema(typing.TypedDict):
    """
    Schema for creating a new conversation model.

    Attributes:
        model_name (str): Name of the LLM model offered by OpenAI, Cloudflare or vLLM.

        api_key (str): The LLM service's API Key.

        system_prompt (str): The system prompt that contains special instructions to the LLM.

        max_bytes (int): The maximum number of bytes to send to the LLM in every API call.
         Consult the LLM's documentation on the number of bytes supported in the context window.

        history_collection (str): Typesense collection that stores the historical conversations.

        account_id (str): LLM service's account ID (only applicable for Cloudflare).

        ttl (int): Time interval in seconds after which the messages would be deleted. Default: 86400 (24 hours).

        vllm_url (str): The URL of the vLLM service.

        id (str): The custom ID of the model.
    """

    id: typing.NotRequired[str]
    model_name: str
    api_key: str
    system_prompt: typing.NotRequired[str]
    max_bytes: int
    history_collection: str
    account_id: typing.NotRequired[str]
    ttl: typing.NotRequired[int]
    vllm_url: typing.NotRequired[str]


class ConversationModelDeleteSchema(typing.TypedDict):
    """
    Schema for deleting a conversation model.

    Attributes:
        id (str): The ID of the model.
    """

    id: str


class ConversationModelSchema(
    ConversationModelCreateSchema,
):
    """
    Schema for a conversation model.

    Attributes:
        model_name (str): Name of the LLM model offered by OpenAI, Cloudflare or vLLM.

        api_key (str): The LLM service's API Key.

        system_prompt (str): The system prompt that contains special instructions to the LLM.

        max_bytes (int): The maximum number of bytes to send to the LLM in every API call.
         Consult the LLM's documentation on the number of bytes supported in the context window.

        history_collection (str): Typesense collection that stores the historical conversations.

        account_id (str): LLM service's account ID (only applicable for Cloudflare).

        ttl (int): Time interval in seconds after which the messages would be deleted. Default: 86400 (24 hours).

        vllm_url (str): The URL of the vLLM service.

        id (str): The custom ID of the model.
    """
