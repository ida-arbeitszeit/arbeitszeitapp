from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from uuid import UUID

from injector import inject

from arbeitszeit.price_calculator import calculate_price
from arbeitszeit.repositories import PlanCooperationRepository, PlanRepository


@dataclass
class PlanSummarySuccess:
    plan_id: UUID
    is_active: bool
    planner_id: UUID
    product_name: str
    description: str
    timeframe: int
    production_unit: str
    amount: int
    means_cost: Decimal
    resources_cost: Decimal
    labour_cost: Decimal
    is_public_service: bool
    price_per_unit: Decimal
    is_available: bool


PlanSummaryResponse = Optional[PlanSummarySuccess]


@inject
@dataclass
class GetPlanSummary:
    plan_repository: PlanRepository
    plan_cooperation_repository: PlanCooperationRepository

    def __call__(self, plan_id: UUID) -> PlanSummaryResponse:
        plan = self.plan_repository.get_plan_by_id(plan_id)
        if plan is None:
            return None
        price_per_unit = calculate_price(
            self.plan_cooperation_repository.get_cooperating_plans(plan.id)
        )
        return PlanSummarySuccess(
            plan_id=plan.id,
            is_active=plan.is_active,
            planner_id=plan.planner.id,
            product_name=plan.prd_name,
            description=plan.description,
            timeframe=plan.timeframe,
            production_unit=plan.prd_unit,
            amount=plan.prd_amount,
            means_cost=plan.production_costs.means_cost,
            resources_cost=plan.production_costs.resource_cost,
            labour_cost=plan.production_costs.labour_cost,
            is_public_service=plan.is_public_service,
            price_per_unit=price_per_unit,
            is_available=plan.is_available,
        )
