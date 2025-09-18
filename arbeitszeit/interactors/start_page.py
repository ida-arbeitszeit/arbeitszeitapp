from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.records import Plan
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class StartPageInteractor:
    @dataclass
    class PlanDetail:
        approval_date: datetime
        plan_id: UUID
        product_name: str

    @dataclass
    class Response:
        latest_plans: List[StartPageInteractor.PlanDetail]

    database_gateway: DatabaseGateway
    datetime_service: DatetimeService

    def show_start_page(self) -> Response:
        now = self.datetime_service.now()
        latest_plans = [
            self._get_plan(plan)
            for plan in self.database_gateway.get_plans()
            .that_will_expire_after(now)
            .that_were_approved_before(now)
            .ordered_by_creation_date(ascending=False)
            .limit(3)
        ]
        return self.Response(latest_plans=latest_plans)

    def _get_plan(self, plan: Plan) -> PlanDetail:
        assert plan.approval_date
        return self.PlanDetail(
            approval_date=plan.approval_date,
            plan_id=plan.id,
            product_name=plan.prd_name,
        )
