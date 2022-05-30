from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from uuid import UUID

from injector import inject

from arbeitszeit.entities import Plan
from arbeitszeit.price_calculator import calculate_price
from arbeitszeit.repositories import PlanCooperationRepository


@dataclass
class PlanSummary:
    plan_id: UUID
    is_active: bool
    planner_id: UUID
    planner_name: str
    product_name: str
    description: str
    timeframe: int
    active_days: int
    production_unit: str
    amount: int
    means_cost: Decimal
    resources_cost: Decimal
    labour_cost: Decimal
    is_public_service: bool
    price_per_unit: Decimal
    is_available: bool
    is_cooperating: bool
    cooperation: Optional[UUID]


@inject
@dataclass
class PlanSummaryService:
    plan_cooperation_repository: PlanCooperationRepository

    def get_summary_from_plan(self, plan: Plan) -> PlanSummary:
        price_per_unit = calculate_price(
            self.plan_cooperation_repository.get_cooperating_plans(plan.id)
        )
        return PlanSummary(
            plan_id=plan.id,
            is_active=plan.is_active,
            planner_id=plan.planner.id,
            planner_name=plan.planner.name,
            product_name=plan.prd_name,
            description=plan.description,
            timeframe=plan.timeframe,
            active_days=plan.active_days or 0,
            production_unit=plan.prd_unit,
            amount=plan.prd_amount,
            means_cost=plan.production_costs.means_cost,
            resources_cost=plan.production_costs.resource_cost,
            labour_cost=plan.production_costs.labour_cost,
            is_public_service=plan.is_public_service,
            price_per_unit=price_per_unit,
            is_available=plan.is_available,
            is_cooperating=bool(plan.cooperation),
            cooperation=plan.cooperation or None,
        )
