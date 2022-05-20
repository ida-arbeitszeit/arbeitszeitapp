from __future__ import annotations

from dataclasses import dataclass
from typing import List

from arbeitszeit.use_cases.get_latest_activated_plans import GetLatestActivatedPlans
from arbeitszeit_web.url_index import PlanSummaryUrlIndex


@dataclass
class GetLatestActivatedPlansPresenter:
    @dataclass
    class PlanDetailsWeb:
        prd_name: str
        activation_date: str
        plan_summary_url: str

    @dataclass
    class ViewModel:
        plans: List[GetLatestActivatedPlansPresenter.PlanDetailsWeb]

    url_index: PlanSummaryUrlIndex

    def show_latest_plans(
        self, use_case_response: GetLatestActivatedPlans.Response
    ) -> ViewModel:
        return self.ViewModel(
            plans=[
                self._get_plan_details_web(plan_detail)
                for plan_detail in use_case_response.plans
            ]
        )

    def _get_plan_details_web(
        self, plan: GetLatestActivatedPlans.PlanDetail
    ) -> PlanDetailsWeb:
        return self.PlanDetailsWeb(
            prd_name=plan.prd_name,
            activation_date=f"{plan.activation_date}",
            plan_summary_url=self.url_index.get_plan_summary_url(plan.plan_id),
        )
