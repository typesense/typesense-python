"""Types for the debug endpoint."""

import sys

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing


class DebugResponseSchema(typing.TypedDict):
    """
    Response schema for the debug endpoint.

    Attributes:
        state (int): The state of the Typesense server.
        version (str): The version of the Typesense server.
    """

    state: int
    version: str
