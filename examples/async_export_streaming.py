import asyncio
import json
import os
import sys

curr_dir = os.path.dirname(os.path.realpath(__file__))
repo_root = os.path.abspath(os.path.join(curr_dir, os.pardir))
sys.path.insert(1, os.path.join(repo_root, "src"))

import typesense

COLLECTION = "async_export_streaming_books"


async def main() -> None:
    async with typesense.AsyncClient(
        {
            "api_key": os.environ.get("TYPESENSE_API_KEY", "xyz"),
            "nodes": [{"host": "localhost", "port": "8108", "protocol": "http"}],
            "connection_timeout_seconds": 10,
        }
    ) as client:
        await client.collections.create(
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
            await documents.import_(
                [{"id": str(year), "title": f"Book {year}", "year": year} for year in range(2000, 2010)],
                {"action": "create"},
            )

            # Read one document at a time. The stream is closed when the block ends,
            # even if the loop stops early.
            async with await documents.export_stream(
                {"filter_by": "year:>=2005", "batch_size": 100},
            ) as stream:
                async for line in stream:
                    print(json.loads(line)["title"])

            # Count the bytes without keeping the export in memory.
            size = 0
            async with await documents.export_stream() as stream:
                async for chunk in stream.aiter_bytes():
                    size += len(chunk)
            print(f"Read {size} bytes")
        finally:
            await client.collections[COLLECTION].delete()


if __name__ == "__main__":
    asyncio.run(main())
