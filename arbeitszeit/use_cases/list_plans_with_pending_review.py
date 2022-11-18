from __future__ import annotations

from dataclasses import dataclass
from typing import List
from uuid import UUID

from injector import inject

from arbeitszeit.repositories import PlanRepository


@inject
@dataclass
class ListPlansWithPendingReviewUseCase:
    class Request:
        pass

    @dataclass
    class Plan:
        id: UUID
        product_name: str
        planner_name: str

    @dataclass
    class Response:
        plans: List[ListPlansWithPendingReviewUseCase.Plan]

    plan_repository: PlanRepository

    def list_plans_with_pending_review(self, request: Request) -> Response:
        return self.Response(
            plans=[
                self._get_info_for_plan(plan)
                for plan in self.plan_repository.get_all_plans_without_completed_review()
            ]
        )

    def _get_info_for_plan(self, plan: UUID) -> Plan:
        plan_model = self.plan_repository.get_all_plans().with_id(plan).first()
        assert plan_model
        return self.Plan(
            id=plan,
            product_name=plan_model.prd_name,
            planner_name=plan_model.planner.name,
        )
