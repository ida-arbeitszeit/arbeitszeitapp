from typing import Protocol


class ControlThresholds(Protocol):
    def get_allowed_overdraw_of_member_account(self) -> int:
        """-1 means that member accounts can be overdrawn without limit."""
        ...

    def get_acceptable_relative_account_deviation(self) -> int: ...
