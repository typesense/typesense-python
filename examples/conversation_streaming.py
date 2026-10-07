import os
import sys
import typing
import uuid

curr_dir = os.path.dirname(os.path.realpath(__file__))
repo_root = os.path.abspath(os.path.join(curr_dir, os.pardir))
sys.path.insert(1, os.path.join(repo_root, "src"))

import typesense

from typesense.types.document import (
    MessageChunk,
    SearchResponse,
    StreamConfigBuilder,
)


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


typesense_api_key = require_env("TYPESENSE_API_KEY")
openai_api_key = require_env("OPENAI_API_KEY")

run_id = uuid.uuid4().hex
history_collection = f"streaming_history_{run_id}"
documents_collection = f"streaming_docs_{run_id}"
model_id = f"streaming_model_{run_id}"

client = typesense.Client(
    {
        "api_key": typesense_api_key,
        "nodes": [
            {
                "host": "localhost",
                "port": "8108",
                "protocol": "http",
            }
        ],
        "connection_timeout_seconds": 10,
    }
)

client.collections.create(
    {
        "name": history_collection,
        "fields": [
            {"name": "conversation_id", "type": "string"},
            {"name": "model_id", "type": "string"},
            {"name": "timestamp", "type": "int32"},
            {"name": "role", "type": "string", "index": False},
            {"name": "message", "type": "string", "index": False},
        ],
    }
)

client.collections.create(
    {
        "name": documents_collection,
        "fields": [
            {"name": "title", "type": "string"},
            {
                "name": "embedding",
                "type": "float[]",
                "embed": {
                    "from": ["title"],
                    "model_config": {
                        "model_name": "openai/text-embedding-3-small",
                        "api_key": openai_api_key,
                    },
                },
            },
        ],
    }
)

client.collections[documents_collection].documents.create(
    {"id": "stream-1", "title": "Company profile: a developer tools firm."}
)
client.collections[documents_collection].documents.create(
    {"id": "stream-2", "title": "Internal memo about a quarterly planning meeting."}
)

conversation_model = client.conversations_models.create(
    {
        "id": model_id,
        "model_name": "openai/gpt-4o-mini",
        "history_collection": history_collection,
        "api_key": openai_api_key,
        "system_prompt": (
            "You are an assistant for question-answering. "
            "Only use the provided context. Add some fluff about you Being an assistant built for Typesense Conversational Search and a brief overview of how it works"
        ),
        "max_bytes": 16384,
    }
)

search_parameters = {
    "q": "What is this document about?",
    "query_by": "embedding",
    "exclude_fields": "embedding",
    "prefix": False,
    "conversation_model_id": conversation_model["id"],
}

# Iterate over the answer as it is generated, then read the search response.
with client.collections[documents_collection].documents.search_stream(
    search_parameters,
) as answer_stream:
    for chunk in answer_stream:
        print(chunk["message"], end="", flush=True)
    response = answer_stream.get_final_response()
print("\n---\nFound", response["found"], "documents")

# Or pass callbacks to search(), which returns the search response at the end.
stream_config: StreamConfigBuilder[SearchResponse[typing.Any]] = StreamConfigBuilder()


@stream_config.on_chunk
def on_chunk(chunk: MessageChunk) -> None:
    print(chunk["message"], end="", flush=True)


@stream_config.on_complete
def on_complete(response: SearchResponse[typing.Any]) -> None:
    print("\n---\nComplete response keys:", response.keys())


client.collections[documents_collection].documents.search(
    {
        **search_parameters,
        "conversation": True,
        "conversation_stream": True,
        "stream_config": stream_config,
    }
)
