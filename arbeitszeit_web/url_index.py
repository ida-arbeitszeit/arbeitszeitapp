"""This module contains interfaces for getting urls. Please note that
there is legacy code in this module. In the past we used to implement
individual interfaces for different "kinds" of urls. This is now
deprecated and unwanted. If you want to add a new url to the index,
simply add an appropriate method the the UrlIndex interface. If you
need different urls for different roles include the user role in the
arguments of the declared method.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Protocol
from uuid import UUID

from arbeitszeit_web.session import Session, UserRole


class UrlIndex(Protocol):
    def get_member_dashboard_url(self) -> str:
        ...

    def get_plan_summary_url(
        self, *, user_role: Optional[UserRole], plan_id: UUID
    ) -> str:
        ...

    def get_work_invite_url(self, invite_id: UUID) -> str:
        ...

    def get_company_summary_url(
        self, user_role: Optional[UserRole], company_id: UUID
    ) -> str:
        ...

    def get_coop_summary_url(
        self, *, user_role: Optional[UserRole], coop_id: UUID
    ) -> str:
        ...

    def get_company_dashboard_url(self) -> str:
        ...

    def get_draft_summary_url(self, draft_id: UUID) -> str:
        ...

    def get_delete_draft_url(self, draft_id: UUID) -> str:
        ...

    def get_answer_company_work_invite_url(self, invite_id: UUID) -> str:
        ...

    def get_global_barplot_for_certificates_url(
        self, certificates_count: Decimal, available_product: Decimal
    ) -> str:
        ...

    def get_global_barplot_for_means_of_production_url(
        self, planned_means: Decimal, planned_resources: Decimal, planned_work: Decimal
    ) -> str:
        ...

    def get_global_barplot_for_plans_url(
        self, productive_plans: int, public_plans: int
    ) -> str:
        ...

    def get_line_plot_of_company_prd_account(self, company_id: UUID) -> str:
        ...

    def get_line_plot_of_company_r_account(self, company_id: UUID) -> str:
        ...

    def get_line_plot_of_company_p_account(self, company_id: UUID) -> str:
        ...

    def get_line_plot_of_company_a_account(self, company_id: UUID) -> str:
        ...

    def get_pay_consumer_product_url(self, amount: int, plan_id: UUID) -> str:
        ...

    def get_pay_means_of_production_url(self, plan_id: Optional[UUID] = None) -> str:
        ...

    def get_toggle_availability_url(self, plan_id: UUID) -> str:
        ...

    def get_end_coop_url(self, *, plan_id: UUID, cooperation_id: UUID) -> str:
        ...

    def get_request_coop_url(self) -> str:
        ...

    def get_accountant_dashboard_url(self) -> str:
        ...

    def get_my_plans_url(self) -> str:
        ...

    def get_my_plan_drafts_url(self) -> str:
        ...

    def get_file_plan_url(self, draft_id: UUID) -> str:
        ...

    def get_unreviewed_plans_list_view_url(self) -> str:
        ...

    def get_approve_plan_url(self, plan_id: UUID) -> str:
        ...

    def get_create_draft_url(self) -> str:
        ...

    def get_member_confirmation_url(self, *, token: str) -> str:
        ...

    def get_company_confirmation_url(self, *, token: str) -> str:
        ...

    def get_member_query_plans_url(self) -> str:
        ...

    def get_company_query_plans_url(self) -> str:
        ...

    def get_member_query_companies_url(self) -> str:
        ...

    def get_company_query_companies_url(self) -> str:
        ...

    def get_unconfirmed_member_url(self) -> str:
        ...


class RenewPlanUrlIndex(Protocol):
    def get_renew_plan_url(self, plan_id: UUID) -> str:
        ...


class HidePlanUrlIndex(Protocol):
    def get_hide_plan_url(self, plan_id: UUID) -> str:
        ...


class AccountantInvitationUrlIndex(Protocol):
    def get_accountant_invitation_url(self, token: str) -> str:
        ...


class LanguageChangerUrlIndex(Protocol):
    def get_language_change_url(self, language_code: str) -> str:
        ...


@dataclass
class UserUrlIndex:
    """This class is not an interface and therefore should not be
    implemented by the web framework. It is merely used internally as
    a convinience interface. You should refrain from using this class
    in your tests and instead rely on the UrlIndex interface. In a
    test scenario you most likely know in advance if you expect a url
    intended for a member, company or any other role. This is why the
    UrlIndex interface is much better suited for testing needs.
    """

    session: Session
    url_index: UrlIndex

    def get_plan_summary_url(self, plan_id: UUID) -> str:
        user_role = self.session.get_user_role()
        return self.url_index.get_plan_summary_url(user_role=user_role, plan_id=plan_id)
