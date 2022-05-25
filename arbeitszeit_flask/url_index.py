from decimal import Decimal
from uuid import UUID

from flask import url_for


class GeneralUrlIndex:
    def get_accountant_invitation_url(self, token: str) -> str:
        return url_for("auth.signup_accountant", token=token)

    def get_accountant_dashboard_url(self) -> str:
        return url_for("main_accountant.dashboard")


class MemberUrlIndex:
    def get_plan_summary_url(self, plan_id: UUID) -> str:
        return url_for("main_member.plan_summary", plan_id=plan_id)

    def get_message_url(self, message_id: UUID) -> str:
        return url_for("main_member.read_message", message_id=message_id)

    def get_coop_summary_url(self, coop_id: UUID) -> str:
        return url_for("main_member.coop_summary", coop_id=coop_id)

    def get_toggle_availability_url(self, plan_id: UUID) -> str:
        ...

    def get_renew_plan_url(self, plan_id: UUID) -> str:
        ...

    def get_hide_plan_url(self, plan_id: UUID) -> str:
        ...

    def get_request_coop_url(self) -> str:
        ...

    def get_end_coop_url(self, plan_id: UUID, cooperation_id: UUID) -> str:
        ...

    def get_company_summary_url(self, company_id: UUID) -> str:
        return url_for("main_member.company_summary", company_id=company_id)

    def get_invite_url(self, invite_id: UUID) -> str:
        return url_for("main_member.show_company_work_invite", invite_id=invite_id)

    def get_answer_company_work_invite_url(self, invite_id: UUID) -> str:
        return url_for("main_member.show_company_work_invite", invite_id=invite_id)

    def get_list_messages_url(self) -> str:
        return url_for("main_member.list_messages")

    def get_confirmation_url(self, token: str) -> str:
        return url_for(
            endpoint="auth.confirm_email_member", token=token, _external=True
        )


class CompanyUrlIndex:
    def get_plan_summary_url(self, plan_id: UUID) -> str:
        return url_for("main_company.plan_summary", plan_id=plan_id)

    def get_message_url(self, message_id: UUID) -> str:
        return url_for("main_company.read_message", message_id=message_id)

    def get_coop_summary_url(self, coop_id: UUID) -> str:
        return url_for("main_company.coop_summary", coop_id=coop_id)

    def get_toggle_availability_url(self, plan_id: UUID) -> str:
        return url_for("main_company.toggle_availability", plan_id=plan_id)

    def get_renew_plan_url(self, plan_id: UUID) -> str:
        return url_for("main_company.create_draft", expired_plan_id=plan_id)

    def get_hide_plan_url(self, plan_id: UUID) -> str:
        return url_for("main_company.hide_plan", plan_id=plan_id)

    def get_request_coop_url(self) -> str:
        return url_for("main_company.request_cooperation")

    def get_end_coop_url(self, plan_id: UUID, cooperation_id: UUID) -> str:
        return url_for(
            "main_company.end_cooperation",
            plan_id=plan_id,
            cooperation_id=cooperation_id,
        )

    def get_company_summary_url(self, company_id: UUID) -> str:
        return url_for("main_company.company_summary", company_id=company_id)

    def get_invite_url(self, invite_id: UUID) -> str:
        # since invites don't make sense for a company, we redirect
        # them in this case to their dashboard page.
        return url_for("main_company.dashboard")

    def get_answer_company_work_invite_url(self, invite_id: UUID) -> str:
        # since invites don't make sense for a company, we redirect
        # them in this case to their dashboard page.
        return url_for("main_company.dashboard", invite_id=invite_id)

    def get_list_messages_url(self) -> str:
        return url_for("main_company.list_messages")

    def get_confirmation_url(self, token: str) -> str:
        return url_for(
            endpoint="auth.confirm_email_company", token=token, _external=True
        )


class FlaskPlotsUrlIndex:
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
