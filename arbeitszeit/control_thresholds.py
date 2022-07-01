from typing import Protocol


class ControlThresholds(Protocol):
    def get_allowed_overdraw_of_member_account(self) -> int:
        ...

    def get_acceptable_relative_account_deviation(self) -> int:
        ...
