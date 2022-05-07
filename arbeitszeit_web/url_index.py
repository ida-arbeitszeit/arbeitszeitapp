from typing import Protocol
from uuid import UUID


class AnswerCompanyWorkInviteUrlIndex(Protocol):
    def get_answer_company_work_invite_url(self, invite_id: UUID) -> str:
        ...


class InviteUrlIndex(Protocol):
    def get_invite_url(self, invite_id: UUID) -> str:
        ...


class PlanSummaryUrlIndex(Protocol):
    def get_plan_summary_url(self, plan_id: UUID) -> str:
        ...


class MessageUrlIndex(Protocol):
    def get_message_url(self, message_id: UUID) -> str:
        ...


class CoopSummaryUrlIndex(Protocol):
    def get_coop_summary_url(self, coop_id: UUID) -> str:
        ...


class TogglePlanAvailabilityUrlIndex(Protocol):
    def get_toggle_availability_url(self, plan_id: UUID) -> str:
        ...


class RenewPlanUrlIndex(Protocol):
    def get_renew_plan_url(self, plan_id: UUID) -> str:
        ...


class HidePlanUrlIndex(Protocol):
    def get_hide_plan_url(self, plan_id: UUID) -> str:
        ...


class EndCoopUrlIndex(Protocol):
    def get_end_coop_url(self, plan_id: UUID, cooperation_id: UUID) -> str:
        ...


class CompanySummaryUrlIndex(Protocol):
    def get_company_summary_url(self, company_id: UUID) -> str:
        ...


class ListMessagesUrlIndex(Protocol):
    def get_list_messages_url(self) -> str:
        ...


class ConfirmationUrlIndex(Protocol):
    def get_confirmation_url(self, token: str) -> str:
        ...


class AccountantInvitationUrlIndex(Protocol):
    def get_accountant_invitation_url(self, token: str) -> str:
        ...
