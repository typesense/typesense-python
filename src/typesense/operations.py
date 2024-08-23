import sys

from typesense.types.operations import (
    HealthCheckResponse,
    LogSlowRequestsTimeParams,
    OperationResponse,
    SnapshotParameters,
)

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

from typesense import configuration
from typesense.api_call import ApiCall
from typesense.configuration import Configuration


class Operations(object):
    RESOURCE_PATH = "/operations"
    HEALTH_PATH = "/health"
    CONFIG_PATH = "/config"

    def __init__(self, api_call: ApiCall):
        self.api_call = api_call

    @staticmethod
    def _endpoint_path(operation_name: str) -> str:
        return "{0}/{1}".format(Operations.RESOURCE_PATH, operation_name)

    @typing.overload
    def perform(
        self,
        operation_name: typing.Literal["vote"],
        query_params: None = None,
    ) -> OperationResponse: ...

    @typing.overload
    def perform(
        self,
        operation_name: typing.Literal["db/compact"],
        query_params: None = None,
    ) -> OperationResponse: ...

    @typing.overload
    def perform(
        self,
        operation_name: typing.Literal["cache/clear"],
        query_params: None = None,
    ) -> OperationResponse: ...

    @typing.overload
    def perform(
        self,
        operation_name: str,
        query_params: typing.Union[typing.Dict[str, str], None] = None,
    ) -> OperationResponse: ...

    @typing.overload
    def perform(
        self,
        operation_name: typing.Literal["snapshot"],
        query_params: SnapshotParameters,
    ) -> OperationResponse: ...

    def perform(
        self,
        operation_name: typing.Union[
            typing.Literal["snapshot, vote, db/compact, cache/clear"], str
        ],
        query_params: typing.Union[
            SnapshotParameters, typing.Dict[str, str], None
        ] = None,
    ) -> OperationResponse:
        response: OperationResponse = self.api_call.post(
            self._endpoint_path(operation_name),
            params=query_params,
            as_json=True,
            entity_type=OperationResponse,
        )
        return response

    def is_healthy(self) -> bool:
        call_resp = self.api_call.get(
            Operations.HEALTH_PATH, as_json=True, entity_type=HealthCheckResponse
        )
        if isinstance(call_resp, typing.Dict):
            is_ok: bool = call_resp.get("ok", False)
        else:
            is_ok = False
        return is_ok

    def toggle_slow_request_log(
        self, data: LogSlowRequestsTimeParams
    ) -> typing.Dict[str, typing.Union[str, bool]]:
        data_dashed = {key.replace("_", "-"): value for key, value in data.items()}
        response: typing.Dict[str, typing.Union[str, bool]] = self.api_call.post(
            Operations.CONFIG_PATH,
            as_json=True,
            entity_type=typing.Dict[str, typing.Union[str, bool]],
            body=data_dashed,
        )
        return response
