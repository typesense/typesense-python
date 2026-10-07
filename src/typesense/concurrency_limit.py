"""
Optional caps on the number of requests a client sends at once.

``AsyncConcurrencyLimit`` is used by the async client and ``ConcurrencyLimit`` by the
sync client (``utils/run-unasync.py`` maps one name to the other). Both are no-ops
when ``max_concurrent_requests`` is ``None``.

Keeping the cap below the httpx pool's ``max_connections`` means requests queue here
instead of in the pool, so a burst of slow requests cannot exhaust the pool and
raise ``httpx.PoolTimeout``.
"""

import asyncio
import sys
import threading
from types import TracebackType

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing


class AsyncConcurrencyLimit:
    """Async context manager that holds a slot for the duration of a request."""

    def __init__(self, max_concurrent_requests: typing.Optional[int]) -> None:
        """
        Initialize the limit.

        Args:
            max_concurrent_requests (Optional[int]): The maximum number of requests
                in flight at once, or ``None`` for no limit.
        """
        self._max_concurrent_requests = max_concurrent_requests
        # Created on first use, inside the running event loop. On Python < 3.10 a
        # semaphore binds to the loop that is current when it is constructed.
        self._semaphore: typing.Optional[asyncio.Semaphore] = None

    async def __aenter__(self) -> None:
        """Wait for a free slot."""
        if self._max_concurrent_requests is None:
            return
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(self._max_concurrent_requests)
        await self._semaphore.acquire()

    async def __aexit__(
        self,
        exc_type: typing.Optional[typing.Type[BaseException]],
        exc_val: typing.Optional[BaseException],
        exc_tb: typing.Optional[TracebackType],
    ) -> None:
        """Release the slot."""
        if self._semaphore is not None:
            self._semaphore.release()


class ConcurrencyLimit:
    """Context manager that holds a slot for the duration of a request."""

    def __init__(self, max_concurrent_requests: typing.Optional[int]) -> None:
        """
        Initialize the limit.

        Args:
            max_concurrent_requests (Optional[int]): The maximum number of requests
                in flight at once, or ``None`` for no limit.
        """
        self._semaphore: typing.Optional[threading.Semaphore] = (
            None
            if max_concurrent_requests is None
            else threading.Semaphore(max_concurrent_requests)
        )

    def __enter__(self) -> None:
        """Wait for a free slot."""
        if self._semaphore is not None:
            self._semaphore.acquire()

    def __exit__(
        self,
        exc_type: typing.Optional[typing.Type[BaseException]],
        exc_val: typing.Optional[BaseException],
        exc_tb: typing.Optional[TracebackType],
    ) -> None:
        """Release the slot."""
        if self._semaphore is not None:
            self._semaphore.release()
