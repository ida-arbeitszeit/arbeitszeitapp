from __future__ import annotations

from dataclasses import dataclass
from typing import List

from arbeitszeit.use_cases.list_plans_with_pending_review import (
    ListPlansWithPendingReviewUseCase as UseCase,
)


class ListPlansWithPendingReviewPresenter:
    @dataclass
    class Plan:
        product_name: str
        planner_name: str

    @dataclass
    class ViewModel:
        show_plan_list: bool
        plans: List[ListPlansWithPendingReviewPresenter.Plan]

    def list_plans_with_pending_review(self, response: UseCase.Response) -> ViewModel:
        return self.ViewModel(
            show_plan_list=bool(response.plans),
            plans=[
                self.Plan(
                    product_name=plan.product_name, planner_name=plan.planner_name
                )
                for plan in response.plans
            ],
        )
