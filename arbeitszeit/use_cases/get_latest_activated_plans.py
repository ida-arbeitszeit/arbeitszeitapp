from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List
from uuid import UUID

from injector import inject

from arbeitszeit.repositories import PlanRepository


@inject
@dataclass
class GetLatestActivatedPlans:
    @dataclass
    class PlanDetail:
        plan_id: UUID
        prd_name: str
        activation_date: datetime

    @dataclass
    class Response:
        plans: List[GetLatestActivatedPlans.PlanDetail]

    plan_repository: PlanRepository

    def __call__(self) -> Response:
        latest_plans = (
            self.plan_repository.get_three_latest_active_plans_ordered_by_activation_date()
        )
        plans = []
        for plan in latest_plans:
            assert plan.activation_date
            plans.append(self.PlanDetail(plan.id, plan.prd_name, plan.activation_date))

        return self.Response(plans)
