from __future__ import annotations

from dataclasses import dataclass
from typing import List

from injector import inject

from arbeitszeit.use_cases.list_plans_with_pending_review import (
    ListPlansWithPendingReviewUseCase as UseCase,
)
from arbeitszeit_web.url_index import UrlIndex


@inject
@dataclass
class ListPlansWithPendingReviewPresenter:
    @dataclass
    class Plan:
        product_name: str
        planner_name: str
        approve_plan_url: str

    @dataclass
    class ViewModel:
        show_plan_list: bool
        plans: List[ListPlansWithPendingReviewPresenter.Plan]

    url_index: UrlIndex

    def list_plans_with_pending_review(self, response: UseCase.Response) -> ViewModel:
        return self.ViewModel(
            show_plan_list=bool(response.plans),
            plans=[
                self.Plan(
                    product_name=plan.product_name,
                    planner_name=plan.planner_name,
                    approve_plan_url=self.url_index.get_approve_plan_url(plan.id),
                )
                for plan in response.plans
            ],
        )
