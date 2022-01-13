from dataclasses import dataclass
from uuid import UUID

from injector import inject

from arbeitszeit.repositories import (
    CompanyRepository,
    PlanCooperationRepository,
    PlanRepository,
)


@dataclass
class CancelCooperationRequestRequest:
    requester_id: UUID
    plan_id: UUID


@inject
@dataclass
class CancelCooperationRequest:
    plan_coop_repo: PlanCooperationRepository
    plan_repo: PlanRepository
    company_repo: CompanyRepository

    def __call__(self, request: CancelCooperationRequestRequest) -> bool:
        plan = self.plan_repo.get_plan_by_id(request.plan_id)
        requester = self.company_repo.get_by_id(request.requester_id)
        assert plan
        assert requester
        if plan.planner != requester:
            return False
        if plan.requested_cooperation is None:
            return False
        self.plan_coop_repo.set_requested_cooperation_to_none(request.plan_id)
        return True
