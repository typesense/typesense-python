"""
HTTP backends the Typesense client can send requests with.

The client builds an ``httpx`` client by default. Users can pass their own client
instead, either from ``httpx`` or from ``httpx2`` (install ``typesense[httpx2]``,
Python 3.10+). ``httpx2`` is Pydantic's maintained continuation of ``httpx``. It
fixes a connection pool leak in ``httpcore`` (encode/httpcore#1093) that can leave
an async client failing every request with ``PoolTimeout``.

``httpx2`` has the same API as ``httpx`` but its own classes, so every
``isinstance`` check and ``except`` clause has to cover both packages. This module
builds those type tuples once, including ``httpx2`` only when it is installed.
"""

import importlib
import sys
from types import ModuleType

import httpx

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

if typing.TYPE_CHECKING:
    import httpx2  # noqa: F401 (used in the string annotations in this module)


def _import_httpx2() -> typing.Optional[ModuleType]:
    """Return the ``httpx2`` module, or ``None`` when it is not installed."""
    # ``import_module`` is typed as returning a module whether or not httpx2 is
    # installed; a plain ``import`` is ``Any`` to mypy when it is missing (Python 3.9).
    try:
        return importlib.import_module("httpx2")
    except ImportError:
        return None


_httpx2 = _import_httpx2()

_BACKENDS: typing.Final[typing.Tuple[ModuleType, ...]] = tuple(
    backend for backend in (httpx, _httpx2) if backend is not None
)

SyncClientType = typing.Union[httpx.Client, "httpx2.Client"]
AsyncClientType = typing.Union[httpx.AsyncClient, "httpx2.AsyncClient"]
ResponseType = typing.Union[httpx.Response, "httpx2.Response"]


def backend_errors(name: str) -> typing.Tuple[typing.Type[Exception], ...]:
    """
    Return the exception class called ``name`` from every installed backend.

    Args:
        name (str): The exception name shared by ``httpx`` and ``httpx2``.

    Returns:
        Tuple[Type[Exception], ...]: The matching classes, for ``except`` clauses.
    """
    return tuple(getattr(backend, name) for backend in _BACKENDS)


# Declared precisely for type checkers so ``isinstance`` narrows to the client
# unions above; at runtime they only contain the backends that are installed.
if typing.TYPE_CHECKING:
    CLIENT_TYPES: typing.Tuple[
        typing.Type[httpx.Client],
        typing.Type["httpx2.Client"],
    ]
    ASYNC_CLIENT_TYPES: typing.Tuple[
        typing.Type[httpx.AsyncClient],
        typing.Type["httpx2.AsyncClient"],
    ]
else:
    CLIENT_TYPES = tuple(backend.Client for backend in _BACKENDS)
    ASYNC_CLIENT_TYPES = tuple(backend.AsyncClient for backend in _BACKENDS)
