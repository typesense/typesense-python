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

# res = typesense.Collections.create({
#   "name": "goodreads_10k",
#   "fields": [
#     {"name": "original_title", "type": "string" },
#     {"name": "author_names", "type": "string[]" },
#     {"name": "authors", "type": "string[]", "facet": True },
#     {"name": "original_publication_year", "type": "int32" },
#     {"name": "publication_year_str", "type": "string", "facet": True },
#     {"name": "ratings_count", "type": "int32" },
#     {"name": "average_rating", "type": "float" },
#     {"name": "image_url", "type": "string" }
#   ],
#   "token_ranking_field": "ratings_count"
# })

res = typesense.Collections.retrieve("goodreads_10k")
print res