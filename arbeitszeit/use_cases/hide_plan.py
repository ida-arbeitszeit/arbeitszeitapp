from dataclasses import dataclass
from uuid import UUID

from injector import inject

from arbeitszeit.repositories import PlanRepository


@dataclass
class HidePlanResponse:
    plan_id: UUID
    is_success: bool


@inject
@dataclass
class HidePlan:
    plan_repository: PlanRepository

    def __call__(self, plan_id: UUID) -> HidePlanResponse:
        plan = self.plan_repository.get_all_plans().with_id(plan_id).first()
        assert plan is not None
        if plan.is_active:
            return HidePlanResponse(plan_id=plan_id, is_success=False)
        self.plan_repository.hide_plan(plan_id)
        return HidePlanResponse(plan_id=plan_id, is_success=True)
