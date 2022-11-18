from dataclasses import dataclass
from typing import List
from uuid import UUID

from injector import inject

from arbeitszeit.entities import Plan
from arbeitszeit.repositories import PlanRepository


@dataclass
class ListedPlan:
    id: UUID
    prd_name: str


@dataclass
class ListPlansResponse:
    plans: List[ListedPlan]


@inject
@dataclass
class ListPlans:
    plan_repository: PlanRepository

    def __call__(self, company_id: UUID) -> ListPlansResponse:
        plans = [
            self._create_plan_response_model(plan)
            for plan in self.plan_repository.get_active_plans().planned_by(company_id)
        ]
        if not plans:
            return ListPlansResponse(plans=[])
        return ListPlansResponse(plans=plans)

    def _create_plan_response_model(self, plan: Plan) -> ListedPlan:
        return ListedPlan(
            id=plan.id,
            prd_name=plan.prd_name,
        )
