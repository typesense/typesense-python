import typesense

client = typesense.Client({
  'api_key': 'abcd',
  'nodes': [{
    'host': 'localhost',
    'port': '8108',
    'protocol': 'http'
  }],
  'connection_timeout_seconds': 2
})

# Drop pre-existing rule if any
try:
    client.analytics.rules['top_queries'].delete()
except Exception as e:
    pass

# Create a new rule
create_response = client.analytics.rules.create({
    "name": "top_queries",
    "type": "popular_queries",
    "params": {
        "source": {
            "collections": ["products"]
        },
        "destination": {
            "collection": "top_queries"
        },
        "limit": 1000
    }
})
print(create_response)

# Try to fetch it back
print(client.analytics.rules['top_queries'].retrieve())

# Update the rule
update_response = client.analytics.rules.upsert('top_queries', {
    "name": "top_queries",
    "type": "popular_queries",
    "params": {
        "source": {
            "collections": ["products"]
        },
        "destination": {
            "collection": "top_queries"
        },
        "limit": 100
    }
})
print(update_response)

# List all rules
print(client.analytics.rules.retrieve())

# Delete the rule
print(client.analytics.rules['top_queries'].delete())
