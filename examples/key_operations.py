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

# Create a new key
key = client.keys.create({"description": "Search-only key.", "actions": ["documents:search"], "collections": ["*"]})
print(key)

# Try to fetch it back
print(client.keys[key['id']].retrieve())

# Generate scoped search key
print(client.keys.generate_scoped_search_key(key['value'], {"filter_by": "user_id:1080"}))

# Delete the key
print(client.keys[key['id']].delete())

# List all keys
print(client.keys.retrieve())
