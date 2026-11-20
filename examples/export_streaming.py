import json
import os
import sys

curr_dir = os.path.dirname(os.path.realpath(__file__))
repo_root = os.path.abspath(os.path.join(curr_dir, os.pardir))
sys.path.insert(1, os.path.join(repo_root, "src"))

import typesense

COLLECTION = "export_streaming_books"

client = typesense.Client(
    {
        "api_key": os.environ.get("TYPESENSE_API_KEY", "xyz"),
        "nodes": [{"host": "localhost", "port": "8108", "protocol": "http"}],
        "connection_timeout_seconds": 10,
    }
)

client.collections.create(
    {
        "name": COLLECTION,
        "fields": [
            {"name": "title", "type": "string"},
            {"name": "year", "type": "int32"},
        ],
    }
)

try:
    documents = client.collections[COLLECTION].documents
    documents.import_(
        [{"id": str(year), "title": f"Book {year}", "year": year} for year in range(2000, 2010)],
        {"action": "create"},
    )

    # Read one document at a time. The stream is closed when the block ends,
    # even if the loop stops early.
    with documents.export_stream({"filter_by": "year:>=2005", "batch_size": 100}) as stream:
        for line in stream:
            print(json.loads(line)["title"])

    # Write the export to a file without keeping it in memory.
    path = f"{COLLECTION}.jsonl"
    with documents.export_stream() as stream, open(path, "wb") as file:
        for chunk in stream.iter_bytes():
            file.write(chunk)
    print(f"Wrote {os.path.getsize(path)} bytes to {path}")
    os.remove(path)
finally:
    client.collections[COLLECTION].delete()
