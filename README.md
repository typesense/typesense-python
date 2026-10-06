# Typesense Python Client

Python client for the Typesense API: https://github.com/typesense/typesense

## Installation

```
$ pip install typesense
```

You can also add `typesense` to your project's `requirements.txt`.

## Usage

You can find some examples [here](https://github.com/typesense/typesense-python/blob/master/examples/collection_operations.py).

See detailed [API documentation](https://typesense.org/api).

## Async usage

Use `AsyncClient` when working in an async runtime:

```python
import asyncio
import typesense


async def main() -> None:
    client = typesense.AsyncClient({
        "api_key": "abcd",
        "nodes": [{"host": "localhost", "port": "8108", "protocol": "http"}],
        "connection_timeout_seconds": 2,
    })

    print(await client.collections.retrieve())
    await client.api_call.aclose()


if __name__ == "__main__":
    asyncio.run(main())
```

See `examples/async_collection_operations.py` for a fuller async walkthrough.

## Using httpx2

The client sends requests with [httpx](https://www.python-httpx.org/) by default. On Python 3.10+ you can pass an [httpx2](https://github.com/pydantic/httpx2) client instead. httpx2 is Pydantic's maintained continuation of httpx, and it fixes a connection pool leak in httpcore ([encode/httpcore#1093](https://github.com/encode/httpcore/issues/1093)) that can leave an `AsyncClient` failing every request with `PoolTimeout` under load.

```
$ pip install "typesense[httpx2]"
```

```python
import httpx2
import typesense

http_client = httpx2.AsyncClient(
    timeout=httpx2.Timeout(2.0),
    limits=httpx2.Limits(max_connections=100, max_keepalive_connections=20),
)
client = typesense.AsyncClient(
    {
        "api_key": "abcd",
        "nodes": [{"host": "localhost", "port": "8108", "protocol": "http"}],
    },
    http_client=http_client,
)
```

`typesense.Client` takes an `httpx2.Client` the same way. The connection pool settings in the config (`pool_timeout_seconds`, `max_connections`, `max_keepalive_connections`) only apply to the default client, so set them on your own client instead. The Typesense client does not close a client you pass in.

## Compatibility

| Typesense Server | typesense-python |
|------------------|------------------|
| \>= v30.0        | \>= v2.0.0       |
| \>= v28.0        | \>= v1.0.0       |
| \>= v26.0        | \>= v0.20.0      |
| \>= v0.25.0      | \>= v0.16.0      |
| \>= v0.23.0      | \>= v0.14.0      |
| \>= v0.21.0      | \>= v0.13.0      |
| \>= v0.20.0      | \>= v0.11.0      |
| \>= v0.19.0      | \>= v0.10.0      |
| \>= v0.17.0      | \>= v0.9.0       |
| \>= v0.16.0      | \>= v0.8.0       |
| \>= v0.15.0      | \>= v0.7.0       |

## Contributing

> [!NOTE]
> Development happens in async-only code; sync code is generated automatically via `utils/run-unasync.py`.

Bug reports and pull requests are welcome on GitHub at [https://github.com/typesense/typesense-python].
If you change any part of the client's source code, run `uv run utils/run-unasync.py` before opening a PR to keep the generated sync files in sync.

## License

`typesense-python` is distributed under the Apache 2 license.
