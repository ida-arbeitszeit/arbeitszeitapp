from dataclasses import dataclass
from uuid import UUID

from injector import inject

from arbeitszeit.repositories import PlanCooperationRepository, PlanRepository


@dataclass
class CancelCooperationSolicitationRequest:
    requester_id: UUID
    plan_id: UUID


@inject
@dataclass
class CancelCooperationSolicitation:
    plan_coop_repo: PlanCooperationRepository
    plan_repo: PlanRepository

    def __call__(self, request: CancelCooperationSolicitationRequest) -> bool:
        plan = self.plan_repo.get_plans().with_id(request.plan_id).first()
        assert plan
        if plan.planner != request.requester_id:
            return False
        if plan.requested_cooperation is None:
            return False
        self.plan_coop_repo.set_requested_cooperation_to_none(request.plan_id)
        return True
