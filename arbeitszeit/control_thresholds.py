from typing import Protocol


class ControlThresholds(Protocol):
    def get_allowed_overdraw_of_member_account(self) -> int | None:
        """Return the allowed overdraw limit in hours. None means unlimited overdraw."""
        ...

    def get_acceptable_relative_account_deviation(self) -> int: ...
