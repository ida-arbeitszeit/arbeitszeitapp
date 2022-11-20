from __future__ import annotations

from dataclasses import dataclass
from typing import List
from uuid import UUID

from injector import inject

from arbeitszeit import entities
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
        planner_id: UUID

    @dataclass
    class Response:
        plans: List[ListPlansWithPendingReviewUseCase.Plan]

    plan_repository: PlanRepository

    def list_plans_with_pending_review(self, request: Request) -> Response:
        return self.Response(
            plans=[
                self._get_info_for_plan(plan)
                for plan in self.plan_repository.get_plans().without_completed_review()
            ]
        )

    def _get_info_for_plan(self, plan_model: entities.Plan) -> Plan:
        return self.Plan(
            id=plan_model.id,
            product_name=plan_model.prd_name,
            planner_name=plan_model.planner.name,
            planner_id=plan_model.planner.id,
        )
