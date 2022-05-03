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
