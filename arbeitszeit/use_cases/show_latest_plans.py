from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List
from uuid import UUID

from injector import inject
from arbeitszeit.repositories import PlanRepository


@inject
@dataclass
class ShowLatestPlans:
    @dataclass
    class Plan:
        activation_date: datetime
        plan_id: UUID
        product_name: str

    @dataclass
    class Response:
        latest_plans: List[ShowLatestPlans.Plan]

    plan_respository: PlanRepository

    def show_plans(self) -> Response:
        latest_plans = [
            self.Plan(
                activation_date=plan.activation_date,
                plan_id=plan.id,
                product_name=plan.prd_name,
            )
            for plan in self.plan_respository.get_three_latest_active_plans_ordered_by_activation_date()
        ]
        return self.Response(latest_plans=latest_plans)
