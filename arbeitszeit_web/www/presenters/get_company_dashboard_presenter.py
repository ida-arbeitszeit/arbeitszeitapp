from __future__ import annotations

from dataclasses import dataclass
from typing import List

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.use_cases.get_company_dashboard import GetCompanyDashboardUseCase
from arbeitszeit_web.session import UserRole
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class GetCompanyDashboardPresenter:
    @dataclass
    class PlanDetailsWeb:
        prd_name: str
        activation_date: str
        plan_details_url: str

    @dataclass
    class ViewModel:
        has_workers: bool
        company_name: str
        company_id: str
        company_email: str
        has_latest_plans: bool
        latest_plans: List[GetCompanyDashboardPresenter.PlanDetailsWeb]

    url_index: UrlIndex
    datetime_service: DatetimeService

    def present(
        self, use_case_response: GetCompanyDashboardUseCase.Response
    ) -> ViewModel:
        latest_plans = [
            self._get_plan_details_web(plan_detail)
            for plan_detail in use_case_response.three_latest_plans
        ]
        return self.ViewModel(
            has_workers=use_case_response.has_workers,
            company_name=use_case_response.company_info.name,
            company_id=str(use_case_response.company_info.id),
            company_email=use_case_response.company_info.email,
            has_latest_plans=bool(use_case_response.three_latest_plans),
            latest_plans=latest_plans,
        )

    def _get_plan_details_web(
        self, plan: GetCompanyDashboardUseCase.Response.LatestPlansDetails
    ) -> PlanDetailsWeb:
        return self.PlanDetailsWeb(
            prd_name=plan.prd_name,
            activation_date=self.datetime_service.format_datetime(
                plan.activation_date, zone="Europe/Berlin", fmt="%d.%m."
            ),
            plan_details_url=self.url_index.get_plan_details_url(
                plan_id=plan.plan_id, user_role=UserRole.company
            ),
        )
