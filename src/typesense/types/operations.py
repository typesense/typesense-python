"""Types for operations."""

import sys

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing


class SnapshotParameters(typing.TypedDict):
    """
    Parameters for creating a snapshot.

    Attributes:
        snapshot_path (str): The path where the snapshot is stored.
    """

    snapshot_path: str


class LogSlowRequestsTimeParams(typing.TypedDict):
    """
    Parameters for logging slow requests.

    Attributes:
        log_slow_requests_time_ms (int): The time in milliseconds to log slow requests.
    """

    log_slow_requests_time_ms: int


class HealthCheckResponse(typing.TypedDict):
    """
    Response schema for the health check.

    Attributes:
        ok (bool): The status of the health check.
    """

    ok: bool


class SchemaChangesResponse(typing.TypedDict):
    """
    Response schema for schema changes.

    Attributes:
        collection (str): The name of the collection.
        validated_docs (int): The number of validated documents.
        altered_docs (int): The number of altered documents
    """

    collection: str
    validated_docs: int
    altered_docs: int


class OperationResponse(typing.TypedDict):
    """
    Response schema for operations.

    Attributes:
        success (bool): The status of the operation.
    """

    success: bool
