from dataclasses import dataclass
from typing import List
from uuid import UUID

from arbeitszeit.entities import Plan
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class ListInboundCoopRequestsRequest:
    coordinator_id: UUID


@dataclass
class ListedInboundCoopRequest:
    coop_id: UUID
    coop_name: str
    plan_id: UUID
    plan_name: str
    planner_name: str
    planner_id: UUID


@dataclass
class ListInboundCoopRequestsResponse:
    cooperation_requests: List[ListedInboundCoopRequest]


@dataclass
class ListInboundCoopRequests:
    database_gateway: DatabaseGateway

    def __call__(
        self, request: ListInboundCoopRequestsRequest
    ) -> ListInboundCoopRequestsResponse:
        if not self._coordinator_exists(request):
            return ListInboundCoopRequestsResponse(cooperation_requests=[])
        cooperation_requests = [
            self._plan_to_response_model(plan)
            for plan in self.database_gateway.get_plans().that_request_cooperation_with_coordinator(
                request.coordinator_id
            )
        ]
        return ListInboundCoopRequestsResponse(
            cooperation_requests=cooperation_requests
        )

    def _coordinator_exists(self, request: ListInboundCoopRequestsRequest) -> bool:
        return bool(
            self.database_gateway.get_companies().with_id(request.coordinator_id)
        )

    def _plan_to_response_model(self, plan: Plan) -> ListedInboundCoopRequest:
        assert plan.requested_cooperation
        requested_cooperation = (
            self.database_gateway.get_cooperations()
            .with_id(plan.requested_cooperation)
            .first()
        )
        assert requested_cooperation
        planner = self.database_gateway.get_companies().with_id(plan.planner).first()
        assert planner
        return ListedInboundCoopRequest(
            coop_id=plan.requested_cooperation,
            coop_name=requested_cooperation.name,
            plan_id=plan.id,
            plan_name=plan.prd_name,
            planner_name=planner.name,
            planner_id=planner.id,
        )
