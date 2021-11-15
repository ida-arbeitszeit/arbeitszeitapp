from typing import Protocol
from uuid import UUID


class UrlIndex(Protocol):
    def get_plan_summary_url(self, plan_id: UUID) -> str:
        ...
