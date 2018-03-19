import typesense

client = typesense.Client({
  'master_node': {
    'host': 'localhost',
    'port': '8108',
    'protocol': 'http',
    'api_key': 'abcd'
  },
  'read_replica_nodes': [{
    'host': 'localhost',
    'port': '9108',
    'protocol': 'http',
    'api_key': 'abcd'
  }],
  'timeout_seconds': 2
})


# Create a collection

create_response = client.collections.create({
  "name": "books",
  "fields": [
    {"name": "title", "type": "string" },
    {"name": "authors", "type": "string[]" },
    {"name": "authors_facet", "type": "string[]", "facet": True },
    {"name": "publication_year", "type": "int32" },
    {"name": "publication_year_facet", "type": "string", "facet": True },
    {"name": "ratings_count", "type": "int32" },
    {"name": "average_rating", "type": "float" },
    {"name": "image_url", "type": "string" }
  ],
  "default_sorting_field": "ratings_count"
})

print(create_response)

# Retrieve the collection we just created

retrieve_response = client.collections['books'].retrieve()
print(retrieve_response)

# Try retrieving all collections
retrieve_all_response = client.collections.retrieve()
print(retrieve_all_response)

# Add a book

hunger_games_book = {
  'id': '1', 'original_publication_year': 2008, 'authors': ['Suzanne Collins'], 'average_rating': 4.34,
  'publication_year': 2008, 'publication_year_facet': '2008', 'authors_facet': ['Suzanne Collins'],
  'title': 'The Hunger Games',
  'image_url': 'https://images.gr-assets.com/books/1447303603m/2767052.jpg', 
  'ratings_count': 4780653 
}

client.collections['books'].documents.create(hunger_games_book)

# Export the documents from a collection

print(client.collections['books'].documents.export())

# Fetch a document in a collection

print(client.collections['books'].documents['1'].retrieve())

# Search for documents in a collection

print(client.collections['books'].documents.search({
    'q': 'hunger',
    'query_by': 'title',
    'sort_by': 'ratings_count:desc'
}))

# Remove a document from a collection

print(client.collections['books'].documents['1'].delete())

# Drop the collection

drop_response = client.collections['books'].delete()
print(drop_response)
