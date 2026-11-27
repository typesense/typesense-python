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
    async with typesense.AsyncClient({
        "api_key": "abcd",
        "nodes": [{"host": "localhost", "port": "8108", "protocol": "http"}],
        "connection_timeout_seconds": 2,
    }) as client:
        print(await client.collections.retrieve())


if __name__ == "__main__":
    asyncio.run(main())
```

See `examples/async_collection_operations.py` for a fuller async walkthrough. Note that if you pass a caller-supplied `http_client`, `AsyncClient` (and `Client`) leaves it open when exiting the context manager or calling `aclose()`/`close()`, so you are responsible for closing it.

## Streaming document exports

`documents.export()` loads the whole export into memory. `documents.export_stream()` reads it as it arrives:

```python
with client.collections["books"].documents.export_stream({"batch_size": 500}) as stream:
    for line in stream:  # str, without the line feed
        document = json.loads(line)

with client.collections["books"].documents.export_stream() as stream, open("books.jsonl", "wb") as file:
    for chunk in stream.iter_bytes():  # decoded bytes
        file.write(chunk)
```

With `AsyncClient`, await the call and use `async with` and `async for`, with `stream.aiter_bytes()` for the bytes:

```python
async with await client.collections["books"].documents.export_stream() as stream:
    async for line in stream:
        document = json.loads(line)
```

A stream can be read once, either as lines or as bytes. Keep these in mind:

- **Always close the stream**, ideally with a context manager. With `max_concurrent_requests` set, a stream that is abandoned before its end permanently uses up one of the open export places below. With the sync client, closing a stream from another thread does not interrupt a read in progress there: that read raises once `stream_read_timeout_seconds` runs out.
- **A failed export has to be restarted.** Nodes are only retried until the response headers arrive. After that, errors such as `httpx.RemoteProtocolError` or `httpx.ReadTimeout` are raised as they are, and exports cannot resume from where they stopped.
- **Keep reading.** If your code stops reading for about 60 seconds, the server drops the connection. `stream_read_timeout_seconds` (default 60) separately limits how long the client waits for the server's next chunk.
- **Lines are raw.** They are not parsed, and the server could write an error message into the body after a successful status, so a line is not guaranteed to be a document.
- **Exports are uncompressed by default.** The server compresses on the thread that handles all other requests, which delays them, especially with a large `batch_size`. Pass `compress=True` if bandwidth matters more. An `Accept-Encoding` in `additional_headers` is always respected.

With `max_concurrent_requests`, an export only takes a slot while it opens, so requests made while reading an export do not wait for it. To keep connections free for those requests, at most `max_connections - max_concurrent_requests` exports can be open at once. Further exports wait for one to close, with no timeout, so an export opened inside another needs a second free place or it waits forever. If `max_concurrent_requests` is not below `max_connections`, no connection can be kept free, so exports are not limited. The limit does not apply to an `http_client` you pass in, because its pool size is unknown.

If your application cancels many requests, prefer [httpx2](#using-httpx2), which fixes a connection pool leak that cancellation can trigger in httpx.

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
