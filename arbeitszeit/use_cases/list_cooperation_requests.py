from dataclasses import dataclass
from typing import List
from uuid import UUID

from injector import inject

from arbeitszeit.entities import Plan
from arbeitszeit.repositories import CompanyRepository, PlanCooperationRepository


@dataclass
class ListCooperationRequestsRequest:
    coordinator_id: UUID


@dataclass
class ListedCoopRequest:
    coop_id: UUID
    coop_name: str
    plan_id: UUID
    plan_name: str
    planner_name: str


@dataclass
class ListCooperationRequestsResponse:
    cooperation_requests: List[ListedCoopRequest]


@inject
@dataclass
class ListCooperationRequests:
    company_repository: CompanyRepository
    plan_cooperation_repository: PlanCooperationRepository

    def __call__(
        self, request: ListCooperationRequestsRequest
    ) -> ListCooperationRequestsResponse:
        if not self._coordinator_exists(request):
            return ListCooperationRequestsResponse(cooperation_requests=[])
        cooperation_requests = [
            self._plan_to_response_model(plan)
            for plan in self.plan_cooperation_repository.get_requests(
                request.coordinator_id
            )
        ]
        return ListCooperationRequestsResponse(
            cooperation_requests=cooperation_requests
        )

    def _coordinator_exists(self, request: ListCooperationRequestsRequest) -> bool:
        coordinator = self.company_repository.get_by_id(request.coordinator_id)
        return bool(coordinator)

    def _plan_to_response_model(self, plan: Plan) -> ListedCoopRequest:
        assert plan.requested_cooperation
        return ListedCoopRequest(
            coop_id=plan.requested_cooperation,
            coop_name=plan.requested_cooperation.name,
            plan_id=plan.id,
            plan_name=plan.prd_name,
            planner_name=plan.planner.name,
        )
