import typesense

typesense.master_node.host = 'localhost'
typesense.master_node.port = 8108
typesense.master_node.protocol = 'http'
typesense.master_node.api_key = 'abcd'

replica1 = typesense.Node()
replica1.host = 'localhost'
replica1.port = 9108
replica1.protocol = 'http'
replica1.api_key = 'abcd'

typesense.read_replica_nodes.append(replica1)

# Create a collection

create_response = typesense.Collections.create({
  "name": "books",
  "fields": [
    {"name": "original_title", "type": "string"},
    {"name": "author_names", "type": "string[]"},
    {"name": "authors", "type": "string[]", "facet": True},
    {"name": "original_publication_year", "type": "int32"},
    {"name": "publication_year_str", "type": "string", "facet": True},
    {"name": "ratings_count", "type": "int32"},
    {"name": "average_rating", "type": "float"},
    {"name": "image_url", "type": "string"}
  ],
  "token_ranking_field": "ratings_count"
})

print(create_response)

# Retrieve the collection we just created

retrieve_response = typesense.Collections.retrieve('books')
print(retrieve_response)

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