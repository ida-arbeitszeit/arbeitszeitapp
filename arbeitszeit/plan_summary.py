from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.price_calculator import PriceCalculator
from arbeitszeit.repositories import DatabaseGateway


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
    creation_date: datetime
    approval_date: Optional[datetime]
    expiration_date: Optional[datetime]


@dataclass
class PlanSummaryService:
    database_gateway: DatabaseGateway
    price_calculator: PriceCalculator
    datetime_service: DatetimeService

    def get_summary_from_plan(self, plan_id: UUID) -> Optional[PlanSummary]:
        now = self.datetime_service.now()
        plan = self.database_gateway.get_plans().with_id(plan_id).first()
        if plan is None:
            return None
        if plan.is_active_as_of(now):
            price_per_unit = self.price_calculator.calculate_cooperative_price(plan)
        else:
            price_per_unit = self.price_calculator.calculate_individual_price(plan)
        planner = self.database_gateway.get_companies().with_id(plan.planner).first()
        assert planner
        return PlanSummary(
            plan_id=plan.id,
            is_active=plan.is_active_as_of(now),
            planner_id=planner.id,
            planner_name=planner.name,
            product_name=plan.prd_name,
            description=plan.description,
            timeframe=plan.timeframe,
            active_days=plan.active_days(now) or 0,
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
            creation_date=plan.plan_creation_date,
            approval_date=plan.approval_date,
            expiration_date=plan.expiration_date,
        )
