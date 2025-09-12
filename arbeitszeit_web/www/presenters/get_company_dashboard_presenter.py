from __future__ import annotations

from dataclasses import dataclass
from typing import List

from arbeitszeit.use_cases.get_company_dashboard import GetCompanyDashboardUseCase
from arbeitszeit_web.formatters.datetime_formatter import DatetimeFormatter
from arbeitszeit_web.session import UserRole
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class GetCompanyDashboardPresenter:
    @dataclass
    class Tile:
        title: str
        subtitle: str
        icon: str
        url: str

    @dataclass
    class PlanDetailsWeb:
        prd_name: str
        approval_date: str
        plan_details_url: str

    @dataclass
    class ViewModel:
        has_workers: bool
        company_name: str
        company_id: str
        company_email: str
        has_latest_plans: bool
        latest_plans: List[GetCompanyDashboardPresenter.PlanDetailsWeb]
        accounts_tile: GetCompanyDashboardPresenter.Tile

    url_index: UrlIndex
    datetime_formatter: DatetimeFormatter
    translator: Translator

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
            accounts_tile=self._create_accounts_tile(use_case_response),
        )

    def _get_plan_details_web(
        self, plan: GetCompanyDashboardUseCase.Response.LatestPlansDetails
    ) -> PlanDetailsWeb:
        return self.PlanDetailsWeb(
            prd_name=plan.prd_name,
            approval_date=self.datetime_formatter.format_datetime(
                plan.approval_date, fmt="%d.%m."
            ),
            plan_details_url=self.url_index.get_plan_details_url(
                plan_id=plan.plan_id, user_role=UserRole.company
            ),
        )

    def _create_accounts_tile(
        self, use_case_response: GetCompanyDashboardUseCase.Response
    ) -> Tile:
        return self.Tile(
            title=self.translator.gettext("Accounts"),
            subtitle=self.translator.gettext("You have four accounts"),
            icon="chart-line",
            url=self.url_index.get_company_accounts_url(
                company_id=use_case_response.company_info.id
            ),
        )
