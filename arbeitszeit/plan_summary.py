from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from uuid import UUID


@dataclass
class BusinessPlanSummary:
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
