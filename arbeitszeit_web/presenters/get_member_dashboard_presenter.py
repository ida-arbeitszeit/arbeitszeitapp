from dataclasses import dataclass
from typing import List

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.use_cases.get_member_dashboard import (
    GetMemberDashboardResponse,
    PlanDetails,
)
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import PlanSummaryUrlIndex


@dataclass
class Workplace:
    name: str
    email: str


@dataclass
class PlanDetailsWeb:
    prd_name: str
    activation_date: str
    plan_summary_url: str


@dataclass
class GetMemberDashboardViewModel:
    member_id: str
    account_balance: str
    email: str
    workplaces: List[Workplace]
    show_workplaces: bool
    show_workplace_registration_info: bool
    welcome_message: str
    three_latest_plans: List[PlanDetailsWeb]
    has_latest_plans: bool


@dataclass
class GetMemberDashboardPresenter:
    translator: Translator
    url_index: PlanSummaryUrlIndex
    datetime_service: DatetimeService

    def present(
        self, use_case_response: GetMemberDashboardResponse
    ) -> GetMemberDashboardViewModel:
        latest_plans = [
            self._get_plan_details_web(plan_detail)
            for plan_detail in use_case_response.three_latest_plans
        ]
        return GetMemberDashboardViewModel(
            member_id=str(use_case_response.id),
            account_balance=self.translator.gettext(
                "%(num).2f hours" % dict(num=use_case_response.account_balance)
            ),
            email=use_case_response.email,
            workplaces=[
                Workplace(
                    name=workplace.workplace_name,
                    email=workplace.workplace_email,
                )
                for workplace in use_case_response.workplaces
            ],
            show_workplaces=bool(use_case_response.workplaces),
            show_workplace_registration_info=not bool(use_case_response.workplaces),
            welcome_message=self.translator.gettext("Welcome, %s!")
            % use_case_response.name,
            three_latest_plans=latest_plans,
            has_latest_plans=bool(latest_plans),
        )

    def _get_plan_details_web(self, plan_detail: PlanDetails) -> PlanDetailsWeb:
        return PlanDetailsWeb(
            prd_name=plan_detail.prd_name,
            activation_date=self.datetime_service.format_datetime(
                date=plan_detail.activation_date,
                zone="Europe/Berlin",
                fmt="%d.%m.",
            ),
            plan_summary_url=self.url_index.get_plan_summary_url(plan_detail.plan_id),
        )
