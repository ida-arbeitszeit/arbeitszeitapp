from __future__ import annotations

from dataclasses import dataclass
from typing import List
from uuid import UUID

from arbeitszeit import records
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class ListPlansWithPendingReviewInteractor:
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
        plans: List[ListPlansWithPendingReviewInteractor.Plan]

    database_gateway: DatabaseGateway

    def list_plans_with_pending_review(self, request: Request) -> Response:
        return self.Response(
            plans=[
                self._get_info_for_plan(plan)
                for plan in self.database_gateway.get_plans().without_completed_review()
            ]
        )

    def _get_info_for_plan(self, plan_model: records.Plan) -> Plan:
        planner = (
            self.database_gateway.get_companies().with_id(plan_model.planner).first()
        )
        assert planner
        return self.Plan(
            id=plan_model.id,
            product_name=plan_model.prd_name,
            planner_name=planner.name,
            planner_id=planner.id,
        )
