from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Plan
from arbeitszeit.repositories import PlanRepository


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
    datetime_service: DatetimeService

    def show_start_page(self) -> Response:
        now = self.datetime_service.now()
        latest_plans = [
            self._get_plan(plan)
            for plan in self.plan_respository.get_plans()
            .that_will_expire_after(now)
            .that_were_activated_before(now)
            .ordered_by_creation_date(ascending=False)
            .limit(3)
        ]
        return self.Response(latest_plans=latest_plans)

    def _get_plan(self, plan: Plan) -> PlanDetail:
        assert plan.activation_date
        return self.PlanDetail(
            activation_date=plan.activation_date,
            plan_id=plan.id,
            product_name=plan.prd_name,
        )
