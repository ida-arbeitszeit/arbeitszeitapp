from typing import Protocol
from uuid import UUID


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
