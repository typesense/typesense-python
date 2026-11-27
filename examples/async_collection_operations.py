import asyncio
import json
import os
import sys

curr_dir = os.path.dirname(os.path.realpath(__file__))
repo_root = os.path.abspath(os.path.join(curr_dir, os.pardir))
sys.path.insert(1, os.path.join(repo_root, "src"))

import typesense
from typesense.exceptions import TypesenseClientError


async def main() -> None:
    async with typesense.AsyncClient(
        {
            "api_key": "xyz",
            "nodes": [
                {
                    "host": "localhost",
                    "port": "8108",
                    "protocol": "http",
                }
            ],
            "connection_timeout_seconds": 2,
        }
    ) as client:
        # Drop pre-existing collection if any
        try:
            await client.collections["books"].delete()
        except Exception:
            pass

        # Create a collection
        create_response = await client.collections.create(
            {
                "name": "books",
                "fields": [
                    {"name": "title", "type": "string"},
                    {"name": "authors", "type": "string[]", "facet": True},
                    {"name": "publication_year", "type": "int32", "facet": True},
                    {"name": "ratings_count", "type": "int32"},
                    {"name": "average_rating", "type": "float"},
                    {"name": "image_url", "type": "string"},
                ],
                "default_sorting_field": "ratings_count",
            }
        )

        print(create_response)

        # Retrieve the collection we just created
        retrieve_response = await client.collections["books"].retrieve()
        print(retrieve_response)

        # Try retrieving all collections
        retrieve_all_response = await client.collections.retrieve()
        print(retrieve_all_response)

        # Add a book
        hunger_games_book = {
            "id": "1",
            "authors": ["Suzanne Collins"],
            "average_rating": 4.34,
            "publication_year": 2008,
            "title": "The Hunger Games",
            "image_url": "https://images.gr-assets.com/books/1447303603m/2767052.jpg",
            "ratings_count": 4780653,
        }

        await client.collections["books"].documents.create(hunger_games_book)

        # Upsert the same document
        print(await client.collections["books"].documents.upsert(hunger_games_book))

        # Or update it
        hunger_games_book_updated = {"id": "1", "average_rating": 4.45}
        print(
            await client.collections["books"]
            .documents["1"]
            .update(hunger_games_book_updated)
        )

        # Try updating with bad data (with coercion enabled)
        hunger_games_book_updated = {"id": "1", "average_rating": "4.55"}
        print(
            await client.collections["books"]
            .documents["1"]
            .update(hunger_games_book_updated, {"dirty_values": "coerce_or_reject"})
        )

        # Export the documents from a collection
        export_output = await client.collections["books"].documents.export()
        print(export_output)

        # Fetch a document in a collection
        print(await client.collections["books"].documents["1"].retrieve())

        # Search for documents in a collection
        print(
            await client.collections["books"].documents.search(
                {
                    "q": "hunger",
                    "query_by": "title",
                    "sort_by": "ratings_count:desc",
                }
            )
        )

        # Make multiple search requests at the same time
        print(
            await client.multi_search.perform(
                {
                    "searches": [
                        {
                            "q": "hunger",
                            "query_by": "title",
                        },
                        {
                            "q": "suzanne",
                            "query_by": "authors",
                        },
                    ]
                },
                {"collection": "books", "sort_by": "ratings_count:desc"},
            )
        )

        # Remove a document from a collection
        print(await client.collections["books"].documents["1"].delete())

        # Import documents into a collection
        docs_to_import = []
        for exported_doc_str in export_output.split("\n"):
            docs_to_import.append(json.loads(exported_doc_str))

        import_results = await client.collections["books"].documents.import_(
            docs_to_import
        )
        print(import_results)

        # Upserting documents
        import_results = await client.collections["books"].documents.import_(
            docs_to_import,
            {
                "action": "upsert",
                "return_id": True,
            },
        )
        print(import_results)

        # Schema change: add optional field
        schema_change = {
            "fields": [{"name": "in_stock", "optional": True, "type": "bool"}]
        }
        print(await client.collections["books"].update(schema_change))

        # Update value matching a filter
        updated_doc = {"publication_year": 2009}
        print(
            await client.collections["books"].documents.update(
                updated_doc, {"filter_by": "publication_year: 2008"}
            )
        )

        # Drop the field
        schema_change = {"fields": [{"name": "in_stock", "drop": True}]}
        print(await client.collections["books"].update(schema_change))

        # Deleting documents matching a filter query
        print(
            await client.collections["books"].documents.delete(
                {"filter_by": "ratings_count: 4780653"}
            )
        )

        # Try importing empty list
        try:
            import_results = await client.collections["books"].documents.import_(
                [], {"action": "upsert"}
            )
            print(import_results)
        except TypesenseClientError:
            print("Detected import of empty document list.")

        # Drop the collection
        drop_response = await client.collections["books"].delete()
        print(drop_response)


if __name__ == "__main__":
    asyncio.run(main())
