from typing import Protocol


class PoliticalDecisions(Protocol):
    def get_allowed_overdraw_of_member_account(self) -> int:
        ...
