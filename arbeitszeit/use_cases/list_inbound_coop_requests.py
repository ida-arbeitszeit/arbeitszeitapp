from dataclasses import dataclass
from typing import List
from uuid import UUID

from arbeitszeit.entities import Plan
from arbeitszeit.repositories import (
    CompanyRepository,
    CooperationRepository,
    PlanRepository,
)


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
    company_repository: CompanyRepository
    plan_repository: PlanRepository
    cooperation_repository: CooperationRepository

    def __call__(
        self, request: ListInboundCoopRequestsRequest
    ) -> ListInboundCoopRequestsResponse:
        if not self._coordinator_exists(request):
            return ListInboundCoopRequestsResponse(cooperation_requests=[])
        cooperation_requests = [
            self._plan_to_response_model(plan)
            for plan in self.plan_repository.get_plans().that_request_cooperation_with_coordinator(
                request.coordinator_id
            )
        ]
        return ListInboundCoopRequestsResponse(
            cooperation_requests=cooperation_requests
        )

    def _coordinator_exists(self, request: ListInboundCoopRequestsRequest) -> bool:
        return bool(
            self.company_repository.get_companies().with_id(request.coordinator_id)
        )

    def _plan_to_response_model(self, plan: Plan) -> ListedInboundCoopRequest:
        assert plan.requested_cooperation
        requested_cooperation_name = self.cooperation_repository.get_cooperation_name(
            plan.requested_cooperation
        )
        assert requested_cooperation_name
        planner = self.company_repository.get_companies().with_id(plan.planner).first()
        assert planner
        return ListedInboundCoopRequest(
            coop_id=plan.requested_cooperation,
            coop_name=requested_cooperation_name,
            plan_id=plan.id,
            plan_name=plan.prd_name,
            planner_name=planner.name,
            planner_id=planner.id,
        )
