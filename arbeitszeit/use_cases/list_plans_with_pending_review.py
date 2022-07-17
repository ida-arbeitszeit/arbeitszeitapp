from __future__ import annotations

from dataclasses import dataclass
from typing import List

from arbeitszeit.repositories import PlanRepository


@dataclass
class ListPlansWithPendingReviewUseCase:
    class Request:
        pass

    class Plan:
        pass

    @dataclass
    class Response:
        plans: List[ListPlansWithPendingReviewUseCase.Plan]

    plan_repository: PlanRepository

    def list_plans_with_pending_review(self, request: Request) -> Response:
        return self.Response(
            plans=[
                self.Plan()
                for _ in self.plan_repository.get_all_plans_without_completed_review()
            ]
        )
