from decimal import Decimal
from typing import Optional
from uuid import UUID

from flask import url_for

from arbeitszeit.records import ConsumptionType
from arbeitszeit_web.session import UserRole


class GeneralUrlIndex:
    def get_plan_details_url(self, user_role: Optional[UserRole], plan_id: UUID) -> str:
        if user_role == UserRole.company:
            return url_for("main_company.plan_details", plan_id=plan_id)
        elif user_role == UserRole.member:
            return url_for("main_member.plan_details", plan_id=plan_id)
        elif user_role == UserRole.accountant:
            return url_for("main_accountant.plan_details", plan_id=plan_id)
        else:
            raise ValueError(f"Plan summary url is unsupported for {user_role}")

    def get_accountant_invitation_url(self, token: str) -> str:
        return url_for("auth.signup_accountant", token=token)

    def get_accountant_dashboard_url(self) -> str:
        return url_for("main_accountant.dashboard")

    def get_company_dashboard_url(self) -> str:
        return url_for("main_company.dashboard")

    def get_member_dashboard_url(self) -> str:
        return url_for("main_member.dashboard")

    def get_language_change_url(self, language_code: str) -> str:
        return url_for("auth.set_language", language=language_code)

    def get_draft_details_url(self, draft_id: UUID) -> str:
        return url_for("main_company.get_draft_details", draft_id=draft_id)

    def get_delete_draft_url(self, draft_id: UUID) -> str:
        return url_for("main_company.delete_draft", draft_id=draft_id)

    def get_work_invite_url(self, invite_id: UUID) -> str:
        return url_for("main_member.show_company_work_invite", invite_id=invite_id)

    def get_coop_summary_url(self, coop_id: UUID) -> str:
        return url_for("main_user.coop_summary", coop_id=coop_id)

    def get_list_of_coordinators_url(self, cooperation_id: UUID) -> str:
        return url_for(
            "main_user.list_coordinators_of_cooperation", coop_id=cooperation_id
        )

    def get_company_summary_url(self, company_id: UUID) -> str:
        return url_for("main_user.company_summary", company_id=company_id)

    def get_answer_company_work_invite_url(
        self, *, invite_id: UUID, is_absolute: bool
    ) -> str:
        return url_for(
            "main_member.show_company_work_invite",
            invite_id=invite_id,
            _external=is_absolute,
        )

    def get_register_private_consumption_url(
        self, amount: Optional[int] = None, plan_id: Optional[UUID] = None
    ) -> str:
        return url_for(
            endpoint="main_member.register_private_consumption",
            amount=amount,
            plan_id=plan_id,
        )

    def get_global_barplot_for_certificates_url(
        self, certificates_count: Decimal, available_product: Decimal
    ) -> str:
        return url_for(
            endpoint="plots.global_barplot_for_certificates",
            certificates_count=str(certificates_count),
            available_product=str(available_product),
        )

    def get_global_barplot_for_means_of_production_url(
        self, planned_means: Decimal, planned_resources: Decimal, planned_work: Decimal
    ) -> str:
        return url_for(
            endpoint="plots.global_barplot_for_means_of_production",
            planned_means=planned_means,
            planned_resources=planned_resources,
            planned_work=planned_work,
        )

    def get_global_barplot_for_plans_url(
        self, productive_plans: int, public_plans: int
    ) -> str:
        return url_for(
            endpoint="plots.global_barplot_for_plans",
            productive_plans=productive_plans,
            public_plans=public_plans,
        )

    def get_line_plot_of_company_prd_account(self, company_id: UUID) -> str:
        return url_for(
            endpoint="plots.line_plot_of_company_prd_account",
            company_id=str(company_id),
        )

    def get_line_plot_of_company_r_account(self, company_id: UUID) -> str:
        return url_for(
            endpoint="plots.line_plot_of_company_r_account",
            company_id=str(company_id),
        )

    def get_line_plot_of_company_p_account(self, company_id: UUID) -> str:
        return url_for(
            endpoint="plots.line_plot_of_company_p_account",
            company_id=str(company_id),
        )

    def get_line_plot_of_company_a_account(self, company_id: UUID) -> str:
        return url_for(
            endpoint="plots.line_plot_of_company_a_account",
            company_id=str(company_id),
        )

    def get_register_productive_consumption_url(
        self,
        plan_id: Optional[UUID] = None,
        amount: Optional[int] = None,
        consumption_type: Optional[ConsumptionType] = None,
    ) -> str:
        if consumption_type == ConsumptionType.means_of_prod:
            type_string = "fixed"
        elif consumption_type == ConsumptionType.raw_materials:
            type_string = "liquid"
        else:
            type_string = None
        return url_for(
            endpoint="main_company.register_productive_consumption",
            plan_id=plan_id,
            amount=amount,
            type_of_consumption=type_string,
        )

    def get_end_coop_url(self, plan_id: UUID, cooperation_id: UUID) -> str:
        return url_for(
            "main_company.end_cooperation",
            plan_id=plan_id,
            cooperation_id=cooperation_id,
        )

    def get_request_coop_url(self) -> str:
        return url_for("main_company.request_cooperation")

    def get_my_plans_url(self) -> str:
        return url_for("main_company.my_plans")

    def get_my_plan_drafts_url(self) -> str:
        return url_for("main_company.my_plans", _anchor="drafts")

    def get_file_plan_url(self, draft_id: UUID) -> str:
        return url_for("main_company.file_plan", draft_id=draft_id)

    def get_revoke_plan_filing_url(self, plan_id: UUID) -> str:
        return url_for("main_company.revoke_plan_filing", plan_id=plan_id)

    def get_unreviewed_plans_list_view_url(self) -> str:
        return url_for("main_accountant.list_plans_with_pending_review")

    def get_approve_plan_url(self, plan_id: UUID) -> str:
        return url_for("main_accountant.approve_plan", plan=plan_id)

    def get_create_draft_url(self) -> str:
        return url_for("main_company.create_draft")

    def get_member_confirmation_url(self, token: str) -> str:
        return url_for(
            endpoint="auth.confirm_email_member", token=token, _external=True
        )

    def get_company_confirmation_url(self, token: str) -> str:
        return url_for(
            endpoint="auth.confirm_email_company", token=token, _external=True
        )

    def get_query_plans_url(self) -> str:
        return url_for(endpoint="main_user.query_plans")

    def get_query_companies_url(self) -> str:
        return url_for(endpoint="main_user.query_companies")

    def get_unconfirmed_member_url(self) -> str:
        return url_for(endpoint="auth.unconfirmed_member")

    def get_unconfirmed_company_url(self) -> str:
        return url_for(endpoint="auth.unconfirmed_company")

    def get_start_page_url(self) -> str:
        return url_for(endpoint="auth.start")

    def get_user_account_details_url(self) -> str:
        return url_for("main_user.account_details")

    def get_renew_plan_url(self, plan_id: UUID) -> str:
        return url_for("main_company.create_draft_from_plan", plan_id=plan_id)

    def get_hide_plan_url(self, plan_id: UUID) -> str:
        return url_for("main_company.hide_plan", plan_id=plan_id)

    def get_request_coordination_transfer_url(self, coop_id: UUID) -> str:
        return url_for("main_company.request_coordination_transfer", coop_id=coop_id)

    def get_show_coordination_transfer_request_url(self, transfer_request: UUID) -> str:
        return url_for(
            "main_company.show_coordination_transfer_request",
            transfer_request=transfer_request,
            _external=True,
        )

    def get_request_change_email_url(self) -> str:
        return url_for("main_user.request_email_change")

    def get_change_email_url(self, *, token: str) -> str:
        return url_for("main_user.change_email_address", token=token, _external=True)

    def get_company_accounts_url(self, *, company_id: UUID) -> str:
        return url_for("main_user.company_accounts", company_id=company_id)

    def get_company_account_p_url(self, *, company_id: UUID) -> str:
        return url_for("main_user.company_account_p", company_id=company_id)

    def get_company_account_r_url(self, *, company_id: UUID) -> str:
        return url_for("main_user.company_account_r", company_id=company_id)

    def get_company_account_a_url(self, *, company_id: UUID) -> str:
        return url_for("main_user.company_account_a", company_id=company_id)

    def get_company_account_prd_url(self, *, company_id: UUID) -> str:
        return url_for("main_user.company_account_prd", company_id=company_id)

    def get_company_transactions_url(self, *, company_id: UUID) -> str:
        return url_for("main_user.get_company_transactions", company_id=company_id)
