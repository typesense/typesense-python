import typesense

typesense.master_node = typesense.Node(host='localhost', port=8108, protocol='http', api_key='abcd')
typesense.read_replica_nodes = [
    typesense.Node(host='localhost', port=9108, protocol='http', api_key='abcd')
]

# Create a collection

create_response = typesense.Collections.create({
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
  "token_ranking_field": "ratings_count"
})

print(create_response)

# Retrieve the collection we just created

retrieve_response = typesense.Collections.retrieve('books')
print(retrieve_response)

# Try retrieving all collections
retrieve_all_response = typesense.Collections.retrieve_all()
print(retrieve_all_response)

# Add a book

hunger_games_book = {
  'id': '1', 'original_publication_year': 2008, 'author_names': ['Suzanne Collins'], 'average_rating': 4.34,                  
  'publication_year_str': '2008', 'authors': ['Suzanne Collins'], 'original_title': 'The Hunger Games', 
  'image_url': 'https://images.gr-assets.com/books/1447303603m/2767052.jpg', 
  'ratings_count': 4780653 
}

typesense.Documents.create('books', hunger_games_book)

# Export the collection

print(typesense.Documents.export('books'))

# Fetch a document

print(typesense.Documents.retrieve('books', '1'))

# Search for documents

print(typesense.Documents.search('books', {
    'q': 'hunger',
    'query_by': 'original_title',
    'sort_by': 'ratings_count:desc'
}))

# Delete a document

print(typesense.Documents.delete('books', '1'))

# Drop the collection

drop_response = typesense.Collections.delete('books')
print(drop_response)
