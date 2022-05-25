from decimal import Decimal
from uuid import UUID


class ListMessageUrlIndexTestImpl:
    def get_list_messages_url(self) -> str:
        return "list messages"


class PlanSummaryUrlIndexTestImpl:
    def get_plan_summary_url(self, plan_id: UUID) -> str:
        return f"fake_plan_url:{plan_id}"


class CoopSummaryUrlIndexTestImpl:
    def get_coop_summary_url(self, coop_id: UUID) -> str:
        return f"fake_coop_url:{coop_id}"


class RequestCoopUrlIndexTestImpl:
    def get_request_coop_url(self) -> str:
        return "fake_request_coop_url"


class EndCoopUrlIndexTestImpl:
    def get_end_coop_url(self, plan_id: UUID, cooperation_id: UUID) -> str:
        return f"fake_end_coop_url:{plan_id}, {cooperation_id}"


class TogglePlanAvailabilityUrlIndex:
    def get_toggle_availability_url(self, plan_id: UUID) -> str:
        return f"fake_toggle_url:{plan_id}"


class CompanySummaryUrlIndex:
    def get_company_summary_url(self, company_id: UUID) -> str:
        return f"fake_company_url:{company_id}"


class MessageUrlIndex:
    def get_message_url(self, message_id: UUID) -> str:
        return f"url:{message_id}"


class AnswerCompanyWorkInviteUrlIndexImpl:
    def get_answer_company_work_invite_url(self, invite_id: UUID) -> str:
        return f"{invite_id} url"


class RenewPlanUrlIndex:
    def get_renew_plan_url(self, plan_id: UUID) -> str:
        return f"fake_renew_url:{plan_id}"


class HidePlanUrlIndex:
    def get_hide_plan_url(self, plan_id: UUID) -> str:
        return f"fake_hide_plan_url:{plan_id}"


class InviteUrlIndexImpl:
    def get_invite_url(self, invite_id: UUID) -> str:
        return f"invite url for {invite_id}"


class ConfirmationUrlIndexImpl:
    def get_confirmation_url(self, token: str) -> str:
        return f"{token} url"


class AccountantInvitationUrlIndexImpl:
    def get_accountant_invitation_url(self, token: str) -> str:
        return f"accountant invitation {token} url"


class PlotsUrlIndexImpl:
    def get_global_barplot_for_certificates_url(
        self, certificates_count: Decimal, available_product: Decimal
    ) -> str:
        return f"barplot url with {certificates_count} and {available_product}"

    def get_global_barplot_for_means_of_production_url(
        self, planned_means: Decimal, planned_resources: Decimal, planned_work: Decimal
    ) -> str:
        return (
            f"barplot url with {planned_means}, {planned_resources} and {planned_work}"
        )

    def get_global_barplot_for_plans_url(
        self, productive_plans: int, public_plans: int
    ) -> str:
        return f"barplot url with {productive_plans} and {public_plans}"

    def get_line_plot_of_company_prd_account(self, company_id: UUID) -> str:
        return f"line plot for {company_id}"

    def get_line_plot_of_company_r_account(self, company_id: UUID) -> str:
        return f"line plot for {company_id}"

    def get_line_plot_of_company_p_account(self, company_id: UUID) -> str:
        return f"line plot for {company_id}"

    def get_line_plot_of_company_a_account(self, company_id: UUID) -> str:
        return f"line plot for {company_id}"


class AccountantDashboardUrlIndexImpl:
    def get_accountant_dashboard_url(self) -> str:
        return "accountant dashboard url"
