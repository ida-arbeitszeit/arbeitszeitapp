from dataclasses import dataclass
from uuid import UUID

from injector import inject

from arbeitszeit.entities import Plan
from arbeitszeit.errors import PlanIsActive
from arbeitszeit.repositories import PlanRepository


@dataclass
class DeletePlanResponse:
    plan_id: UUID


@inject
@dataclass
class DeletePlan:
    plan_repository: PlanRepository

    def __call__(self, plan: Plan) -> DeletePlanResponse:
        if plan.is_active:
            raise PlanIsActive()
        self.plan_repository.delete_plan(plan)

        return DeletePlanResponse(plan_id=plan.id)
