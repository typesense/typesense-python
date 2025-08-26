"""Client for Analytics events and status operations."""

import sys

if sys.version_info >= (3, 11):
    import typing
else:
    import typing_extensions as typing

from typesense.api_call import ApiCall
from typesense.types.analytics import (
    AnalyticsEvent as AnalyticsEventSchema,
    AnalyticsEventCreateResponse,
    AnalyticsEventsResponse,
    AnalyticsStatus,
)


class AnalyticsEvents:
    events_path: typing.Final[str] = "/analytics/events"
    flush_path: typing.Final[str] = "/analytics/flush"
    status_path: typing.Final[str] = "/analytics/status"

    def __init__(self, api_call: ApiCall) -> None:
        self.api_call = api_call

    def create(self, event: AnalyticsEventSchema) -> AnalyticsEventCreateResponse:
        response: AnalyticsEventCreateResponse = self.api_call.post(
            AnalyticsEvents.events_path,
            body=event,
            as_json=True,
            entity_type=AnalyticsEventCreateResponse,
        )
        return response

    def retrieve(
        self,
        *,
        user_id: str,
        name: str,
        n: int,
    ) -> AnalyticsEventsResponse:
        params: typing.Dict[str, typing.Union[str, int]] = {
            "user_id": user_id,
            "name": name,
            "n": n,
        }
        response: AnalyticsEventsResponse = self.api_call.get(
            AnalyticsEvents.events_path,
            params=params,
            as_json=True,
            entity_type=AnalyticsEventsResponse,
        )
        return response

    def flush(self) -> AnalyticsEventCreateResponse:
        response: AnalyticsEventCreateResponse = self.api_call.post(
            AnalyticsEvents.flush_path,
            body={},
            as_json=True,
            entity_type=AnalyticsEventCreateResponse,
        )
        return response

    def status(self) -> AnalyticsStatus:
        response: AnalyticsStatus = self.api_call.get(
            AnalyticsEvents.status_path,
            as_json=True,
            entity_type=AnalyticsStatus,
        )
        return response


