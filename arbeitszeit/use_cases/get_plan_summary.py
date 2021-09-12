from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from injector import inject

from arbeitszeit.repositories import PlanRepository


@dataclass
class PlanSummaryResponse:
    id: UUID
    product_name: str
    description: str
    timeframe: int
    production_unit: str
    amount: int
    means_cost: Decimal
    resources_cost: Decimal
    labour_cost: Decimal
    is_public_service: bool


@inject
@dataclass
class GetPlanSummary:
    plan_repository: PlanRepository

    def __call__(self, plan_id: UUID) -> PlanSummaryResponse:
        plan = self.plan_repository.get_plan_by_id(plan_id)
        return PlanSummaryResponse(
            id=plan_id,
            product_name=plan.prd_name,
            description=plan.description,
            timeframe=plan.timeframe,
            production_unit=plan.prd_unit,
            amount=plan.prd_amount,
            means_cost=plan.production_costs.means_cost,
            resources_cost=plan.production_costs.resource_cost,
            labour_cost=plan.production_costs.labour_cost,
            is_public_service=plan.is_public_service,
        )
