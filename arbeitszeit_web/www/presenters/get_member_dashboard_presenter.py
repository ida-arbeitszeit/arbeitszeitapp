from dataclasses import dataclass
from typing import List

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.use_cases.get_member_dashboard import GetMemberDashboard
from arbeitszeit_web.session import UserRole
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


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
class Invite:
    invite_details_url: str
    invite_message: str


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
    invites: List[Invite]
    show_invites: bool


@dataclass
class GetMemberDashboardPresenter:
    translator: Translator
    url_index: UrlIndex
    datetime_service: DatetimeService

    def present(
        self, use_case_response: GetMemberDashboard.Response
    ) -> GetMemberDashboardViewModel:
        latest_plans = [
            self._get_plan_details_web(plan_detail)
            for plan_detail in use_case_response.three_latest_plans
        ]
        invites = [
            self._get_invites_web(invite) for invite in use_case_response.invites
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
            invites=invites,
            show_invites=bool(invites),
        )

    def _get_plan_details_web(
        self, plan_detail: GetMemberDashboard.PlanDetails
    ) -> PlanDetailsWeb:
        return PlanDetailsWeb(
            prd_name=plan_detail.prd_name,
            activation_date=self.datetime_service.format_datetime(
                date=plan_detail.activation_date,
                zone="Europe/Berlin",
                fmt="%d.%m.",
            ),
            plan_summary_url=self.url_index.get_plan_summary_url(
                user_role=UserRole.member, plan_id=plan_detail.plan_id
            ),
        )

    def _get_invites_web(self, invite: GetMemberDashboard.WorkInvitation) -> Invite:
        return Invite(
            invite_details_url=self.url_index.get_work_invite_url(invite.invite_id),
            invite_message=self.translator.gettext(
                "Company %(company)s has invited you!"
                % dict(company=invite.company_name)
            ),
        )
