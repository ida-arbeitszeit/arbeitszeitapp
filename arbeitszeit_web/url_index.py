from typing import Protocol
from uuid import UUID


class PlanSummaryUrlIndex(Protocol):
    def get_plan_summary_url(self, plan_id: UUID) -> str:
        ...


class MessageUrlIndex(Protocol):
    def get_message_url(self, message_id: UUID) -> str:
        ...
