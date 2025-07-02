"""NLSearchModel types for Typesense Python Client."""

import sys

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing


class NLSearchModelBase(typing.TypedDict):
    """
    Base schema with all possible fields for NL search models.

    Attributes:
        model_name (str): Name of the LLM model.
        api_key (str): The LLM service's API Key.
        api_url (str): The API URL for the LLM service.
        max_bytes (int): The maximum number of bytes to send to the LLM.
        temperature (float): The temperature parameter for the LLM.
        system_prompt (str): The system prompt for the LLM.
        top_p (float): The top_p parameter (Google-specific).
        top_k (int): The top_k parameter (Google-specific).
        stop_sequences (list[str]): Stop sequences for the LLM (Google-specific).
        api_version (str): API version (Google-specific).
        project_id (str): GCP project ID (GCP Vertex AI specific).
        access_token (str): Access token for GCP (GCP Vertex AI specific).
        refresh_token (str): Refresh token for GCP (GCP Vertex AI specific).
        client_id (str): Client ID for GCP (GCP Vertex AI specific).
        client_secret (str): Client secret for GCP (GCP Vertex AI specific).
        region (str): Region for GCP (GCP Vertex AI specific).
        max_output_tokens (int): Maximum output tokens (GCP Vertex AI specific).
        account_id (str): Account ID (Cloudflare specific).
    """

    model_name: str
    api_key: typing.NotRequired[str]
    api_url: typing.NotRequired[str]
    max_bytes: typing.NotRequired[int]
    temperature: typing.NotRequired[float]
    system_prompt: typing.NotRequired[str]
    # Google-specific parameters
    top_p: typing.NotRequired[float]
    top_k: typing.NotRequired[int]
    stop_sequences: typing.NotRequired[typing.List[str]]
    api_version: typing.NotRequired[str]
    # GCP Vertex AI specific
    project_id: typing.NotRequired[str]
    access_token: typing.NotRequired[str]
    refresh_token: typing.NotRequired[str]
    client_id: typing.NotRequired[str]
    client_secret: typing.NotRequired[str]
    region: typing.NotRequired[str]
    max_output_tokens: typing.NotRequired[int]
    # Cloudflare specific
    account_id: typing.NotRequired[str]


class NLSearchModelCreateSchema(NLSearchModelBase):
    """
    Schema for creating a new NL search model.

    Attributes:
        id (str): The custom ID of the model.
    """

    id: typing.NotRequired[str]


class NLSearchModelUpdateSchema(typing.TypedDict):
    """
    Base schema with all possible fields for NL search models.

    Attributes:
        model_name (str): Name of the LLM model.
        api_key (str): The LLM service's API Key.
        api_url (str): The API URL for the LLM service.
        max_bytes (int): The maximum number of bytes to send to the LLM.
        temperature (float): The temperature parameter for the LLM.
        system_prompt (str): The system prompt for the LLM.
        top_p (float): The top_p parameter (Google-specific).
        top_k (int): The top_k parameter (Google-specific).
        stop_sequences (list[str]): Stop sequences for the LLM (Google-specific).
        api_version (str): API version (Google-specific).
        project_id (str): GCP project ID (GCP Vertex AI specific).
        access_token (str): Access token for GCP (GCP Vertex AI specific).
        refresh_token (str): Refresh token for GCP (GCP Vertex AI specific).
        client_id (str): Client ID for GCP (GCP Vertex AI specific).
        client_secret (str): Client secret for GCP (GCP Vertex AI specific).
        region (str): Region for GCP (GCP Vertex AI specific).
        max_output_tokens (int): Maximum output tokens (GCP Vertex AI specific).
        account_id (str): Account ID (Cloudflare specific).
    """

    model_name: typing.NotRequired[str]
    api_key: typing.NotRequired[str]
    api_url: typing.NotRequired[str]
    max_bytes: typing.NotRequired[int]
    temperature: typing.NotRequired[float]
    system_prompt: typing.NotRequired[str]
    # Google-specific parameters
    top_p: typing.NotRequired[float]
    top_k: typing.NotRequired[int]
    stop_sequences: typing.NotRequired[typing.List[str]]
    api_version: typing.NotRequired[str]
    # GCP Vertex AI specific
    project_id: typing.NotRequired[str]
    access_token: typing.NotRequired[str]
    refresh_token: typing.NotRequired[str]
    client_id: typing.NotRequired[str]
    client_secret: typing.NotRequired[str]
    region: typing.NotRequired[str]
    max_output_tokens: typing.NotRequired[int]
    # Cloudflare specific
    account_id: typing.NotRequired[str]


class NLSearchModelDeleteSchema(typing.TypedDict):
    """
    Schema for deleting an NL search model.

    Attributes:
        id (str): The ID of the model.
    """

    id: str


class NLSearchModelSchema(NLSearchModelBase):
    """
    Schema for an NL search model.

    Attributes:
        id (str): The ID of the model.
    """

    id: str


NLSearchModelsRetrieveSchema = typing.List[NLSearchModelSchema]
