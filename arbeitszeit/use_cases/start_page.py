from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List
from uuid import UUID

from injector import inject

from arbeitszeit.entities import Plan
from arbeitszeit.repositories import PlanRepository


@inject
@dataclass
class StartPageUseCase:
    @dataclass
    class PlanDetail:
        activation_date: datetime
        plan_id: UUID
        product_name: str

    @dataclass
    class Response:
        latest_plans: List[StartPageUseCase.PlanDetail]

    plan_respository: PlanRepository

    def show_start_page(self) -> Response:
        latest_plans = [
            self._get_plan(plan)
            for plan in self.plan_respository.get_active_plans().order_by_creation_date(ascending=False).limit(3)
        ]
        return self.Response(latest_plans=latest_plans)

    def _get_plan(self, plan: Plan) -> PlanDetail:
        assert plan.activation_date
        return self.PlanDetail(
            activation_date=plan.activation_date,
            plan_id=plan.id,
            product_name=plan.prd_name,
        )
