from dataclasses import dataclass
from typing import List
from uuid import UUID

from injector import inject

from arbeitszeit.entities import Plan
from arbeitszeit.repositories import (
    CompanyRepository,
    CooperationRepository,
    PlanCooperationRepository,
)


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


@inject
@dataclass
class ListOutboundCoopRequests:
    company_repository: CompanyRepository
    plan_cooperation_repository: PlanCooperationRepository
    cooperation_repository: CooperationRepository

    def __call__(
        self, request: ListOutboundCoopRequestsRequest
    ) -> ListOutboundCoopRequestsResponse:
        if not self._requester_exists(request):
            return ListOutboundCoopRequestsResponse(cooperation_requests=[])
        cooperation_requests = [
            self._plan_to_response_model(plan)
            for plan in self.plan_cooperation_repository.get_outbound_requests(
                request.requester_id
            )
        ]
        return ListOutboundCoopRequestsResponse(
            cooperation_requests=cooperation_requests
        )

    def _requester_exists(self, request: ListOutboundCoopRequestsRequest) -> bool:
        requester = self.company_repository.get_by_id(request.requester_id)
        return bool(requester)

    def _plan_to_response_model(self, plan: Plan) -> ListedOutboundCoopRequest:
        assert plan.requested_cooperation
        requested_cooperation_name = self.cooperation_repository.get_cooperation_name(
            plan.requested_cooperation
        )
        assert requested_cooperation_name
        return ListedOutboundCoopRequest(
            plan_id=plan.id,
            plan_name=plan.prd_name,
            coop_id=plan.requested_cooperation,
            coop_name=requested_cooperation_name,
        )
