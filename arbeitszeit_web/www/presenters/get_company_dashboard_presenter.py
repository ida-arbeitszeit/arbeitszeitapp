from __future__ import annotations

from dataclasses import dataclass
from typing import List

from arbeitszeit.interactors.get_company_dashboard import GetCompanyDashboardInteractor
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
        self, interactor_response: GetCompanyDashboardInteractor.Response
    ) -> ViewModel:
        latest_plans = [
            self._get_plan_details_web(plan_detail)
            for plan_detail in interactor_response.three_latest_plans
        ]
        return self.ViewModel(
            has_workers=interactor_response.has_workers,
            company_name=interactor_response.company_info.name,
            company_id=str(interactor_response.company_info.id),
            company_email=interactor_response.company_info.email,
            has_latest_plans=bool(interactor_response.three_latest_plans),
            latest_plans=latest_plans,
            accounts_tile=self._create_accounts_tile(interactor_response),
        )

    def _get_plan_details_web(
        self, plan: GetCompanyDashboardInteractor.Response.LatestPlansDetails
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
        self, interactor_response: GetCompanyDashboardInteractor.Response
    ) -> Tile:
        return self.Tile(
            title=self.translator.gettext("Accounts"),
            subtitle=self.translator.gettext("You have four accounts"),
            icon="chart-line",
            url=self.url_index.get_company_accounts_url(
                company_id=interactor_response.company_info.id
            ),
        )
