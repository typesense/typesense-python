"""
This module provides functionality for performing various operations in the Typesense API.

It contains the Operations class, which handles different API operations such as
health checks, snapshots, and configuration changes.

Classes:
    Operations: Manages various operations in the Typesense API.

Dependencies:
    - typesense.types.operations:
        Provides type definitions for operation responses and parameters.
    - typesense.api_call: Provides the ApiCall class for making API requests.
    - typesense.configuration: Provides the Configuration class.

Note: This module uses conditional imports to support both Python 3.11+ and earlier versions.
"""

import sys

from typesense.types.operations import (
    HealthCheckResponse,
    LogSlowRequestsTimeParams,
    OperationResponse,
    SchemaChangesResponse,
    SnapshotParameters,
)

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

from typesense.api_call import ApiCall


class Operations:
    """
    Manages various operations in the Typesense API.

    This class provides methods to perform different operations such as
    health checks, snapshots, and configuration changes.

    Attributes:
        resource_path (str): The base path for operations endpoints.
        healht_path (str): The path for the health check endpoint.
        config_path (str): The path for the configuration endpoint.
        api_call (ApiCall): The ApiCall instance for making API requests.
    """

    resource_path: typing.Final[str] = "/operations"
    health_path: typing.Final[str] = "/health"
    config_path: typing.Final[str] = "/config"
    schema_changes: typing.Final[str] = "/schema_changes"

    def __init__(self, api_call: ApiCall):
        """
        Initialize the Operations instance.

        Args:
            api_call (ApiCall): The ApiCall instance for making API requests.
        """
        self.api_call = api_call

    @typing.overload
    def perform(
        self,
        operation_name: typing.Literal["schema_changes"],
        query_params: None = None,
    ) -> typing.List[SchemaChangesResponse]:
        """
        Perform a vote operation.

        Args:
            operation_name (Literal["schema_changes"]): The name of the operation.
            query_params (None, optional): Query parameters (not used for vote operation).

        Returns:
            OperationResponse: The response from the vote operation.
        """

    @typing.overload
    def perform(
        self,
        operation_name: typing.Literal["vote"],
        query_params: None = None,
    ) -> OperationResponse:
        """
        Perform a vote operation.

        Args:
            operation_name (Literal["vote"]): The name of the operation.
            query_params (None, optional): Query parameters (not used for vote operation).

        Returns:
            OperationResponse: The response from the vote operation.
        """

    @typing.overload
    def perform(
        self,
        operation_name: typing.Literal["db/compact"],
        query_params: None = None,
    ) -> OperationResponse:
        """
        Perform a database compaction operation.

        Args:
            operation_name (Literal["db/compact"]): The name of the operation.
            query_params (None, optional): Query parameters (not used for db/compact operation).

        Returns:
            OperationResponse: The response from the database compaction operation.
        """

    @typing.overload
    def perform(
        self,
        operation_name: typing.Literal["cache/clear"],
        query_params: None = None,
    ) -> OperationResponse:
        """
        Perform a cache clear operation.

        Args:
            operation_name (Literal["cache/clear"]): The name of the operation.
            query_params (None, optional):
                Query parameters (not used for cache/clear operation).

        Returns:
            OperationResponse: The response from the cache clear operation.
        """

    @typing.overload
    def perform(
        self,
        operation_name: str,
        query_params: typing.Union[typing.Dict[str, str], None] = None,
    ) -> OperationResponse:
        """
        Perform a generic operation.

        Args:
            operation_name (str): The name of the operation.
            query_params (Union[Dict[str, str], None], optional):
                Query parameters for the operation.

        Returns:
            OperationResponse: The response from the operation.
        """

    @typing.overload
    def perform(
        self,
        operation_name: typing.Literal["snapshot"],
        query_params: SnapshotParameters,
    ) -> OperationResponse:
        """
        Perform a snapshot operation.

        Args:
            operation_name (Literal["snapshot"]): The name of the operation.
            query_params (SnapshotParameters): Query parameters for the snapshot operation.

        Returns:
            OperationResponse: The response from the snapshot operation.
        """

    def perform(
        self,
        operation_name: typing.Union[
            typing.Literal[
                "snapshot",
                "vote",
                "db/compact",
                "cache/clear",
                "schema_changes",
            ],
            str,
        ],
        query_params: typing.Union[
            SnapshotParameters,
            typing.Dict[str, str],
            None,
        ] = None,
    ) -> OperationResponse:
        """
        Perform an operation on the Typesense API.

        This method is the actual implementation for all the overloaded perform methods.

        Args:
            operation_name (Literal["snapshot, vote, db/compact, cache/clear"]):
               The name of the operation to perform.
            query_params (Union[SnapshotParameters, None], optional):
               Query parameters for the operation.

        Returns:
            OperationResponse: The response from the performed operation.
        """
        response: OperationResponse = self.api_call.post(
            self._endpoint_path(operation_name),
            params=query_params,
            as_json=True,
            entity_type=OperationResponse,
        )
        return response

    def is_healthy(self) -> bool:
        """
        Check if the Typesense server is healthy.

        Returns:
            bool: True if the server is healthy, False otherwise.
        """
        call_resp = self.api_call.get(
            Operations.health_path,
            as_json=True,
            entity_type=HealthCheckResponse,
        )
        if isinstance(call_resp, typing.Dict):
            is_ok: bool = call_resp.get("ok", False)
        else:
            is_ok = False
        return is_ok

    def toggle_slow_request_log(
        self,
        log_slow_requests_time_params: LogSlowRequestsTimeParams,
    ) -> typing.Dict[str, typing.Union[str, bool]]:
        """
        Toggle the slow request log configuration.

        Args:
            log_slow_requests_time_params (LogSlowRequestsTimeParams):
               Parameters for configuring slow request logging.

        Returns:
            Dict[str, Union[str, bool]]: The response from the configuration change operation.
        """
        data_dashed = {
            key.replace("_", "-"): dashed_value
            for key, dashed_value in log_slow_requests_time_params.items()
        }
        response: typing.Dict[str, typing.Union[str, bool]] = self.api_call.post(
            Operations.config_path,
            as_json=True,
            entity_type=typing.Dict[str, typing.Union[str, bool]],
            body=data_dashed,
        )
        return response

    @staticmethod
    def _endpoint_path(operation_name: str) -> str:
        """
        Generate the endpoint path for a given operation.

        Args:
            operation_name (str): The name of the operation.

        Returns:
            str: The full endpoint path for the operation.
        """
        return "/".join([Operations.resource_path, operation_name])
