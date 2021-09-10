from dataclasses import dataclass
from uuid import UUID

from injector import inject

from arbeitszeit.entities import Plan
from arbeitszeit.repositories import PlanRepository


@dataclass
class DeletePlanResponse:
    plan_id: UUID
    is_success: bool


@inject
@dataclass
class DeletePlan:
    plan_repository: PlanRepository

    def __call__(self, plan_id: UUID) -> DeletePlanResponse:
        plan = self.plan_repository.get_plan_by_id(plan_id)
        if plan.is_active:
            return DeletePlanResponse(plan_id=plan_id, is_success=False)
        self.plan_repository.delete_plan(plan_id)
        return DeletePlanResponse(plan_id=plan_id, is_success=True)
