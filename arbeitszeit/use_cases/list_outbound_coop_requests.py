from dataclasses import dataclass
from typing import List
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.records import Plan
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class ListOutboundCoopRequestsRequest:
    requester_id: UUID


@dataclass
class ListedOutboundCoopRequest:
    plan_id: UUID
    plan_name: str
    coop_id: UUID
    coop_name: str


@dataclass
class ListOutboundCoopRequestsResponse:
    cooperation_requests: List[ListedOutboundCoopRequest]


@dataclass
class ListOutboundCoopRequests:
    database_gateway: DatabaseGateway
    datetime_service: DatetimeService

    def __call__(
        self, request: ListOutboundCoopRequestsRequest
    ) -> ListOutboundCoopRequestsResponse:
        now = self.datetime_service.now()
        if not self._requester_exists(request):
            return ListOutboundCoopRequestsResponse(cooperation_requests=[])
        plans_with_open_requests = (
            self.database_gateway.get_plans()
            .planned_by(request.requester_id)
            .with_open_cooperation_request()
            .that_will_expire_after(now)
        )
        cooperation_requests = [
            self._plan_to_response_model(plan) for plan in plans_with_open_requests
        ]
        return ListOutboundCoopRequestsResponse(
            cooperation_requests=cooperation_requests
        )

    def _requester_exists(self, request: ListOutboundCoopRequestsRequest) -> bool:
        return bool(self.database_gateway.get_companies().with_id(request.requester_id))

    def _plan_to_response_model(self, plan: Plan) -> ListedOutboundCoopRequest:
        assert plan.requested_cooperation
        requested_cooperation = (
            self.database_gateway.get_cooperations()
            .with_id(plan.requested_cooperation)
            .first()
        )
        assert requested_cooperation
        return ListedOutboundCoopRequest(
            plan_id=plan.id,
            plan_name=plan.prd_name,
            coop_id=plan.requested_cooperation,
            coop_name=requested_cooperation.name,
        )
