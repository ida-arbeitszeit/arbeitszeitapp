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

    @dataclass
    class Response:
        plans: List[ListPlansWithPendingReviewUseCase.Plan]

    plan_repository: PlanRepository

    def list_plans_with_pending_review(self, request: Request) -> Response:
        return self.Response(
            plans=[
                self.Plan(id=plan)
                for plan in self.plan_repository.get_all_plans_without_completed_review()
            ]
        )
