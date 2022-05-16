from dataclasses import dataclass
from datetime import datetime
from typing import List
from uuid import UUID

from injector import inject

from arbeitszeit.repositories import PlanRepository


@dataclass
class PlanDetail:
    plan_id: UUID
    prd_name: str
    activation_date: datetime


@inject
@dataclass
class GetLatestActivatedPlans:
    plan_repository: PlanRepository

    @dataclass
    class Response:
        plans: List[PlanDetail]

    def __call__(self) -> Response:
        latest_plans = self.plan_repository.get_active_plans(
            limit=3, order_by_activation_date=True
        )
        plans = []
        for plan in latest_plans:
            assert plan.activation_date
            plans.append(PlanDetail(plan.id, plan.prd_name, plan.activation_date))

        return self.Response(plans)
