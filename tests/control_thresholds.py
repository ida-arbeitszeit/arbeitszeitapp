from dataclasses import dataclass


@dataclass
class ControlThresholdsTestImpl:
    allowed_overdraw_of_member_account: int = 0
    acceptable_relative_account_deviation: int = 33

    def get_allowed_overdraw_of_member_account(self) -> int:
        return self.allowed_overdraw_of_member_account

    def set_allowed_overdraw_of_member_account(self, overdraw: int) -> None:
        self.allowed_overdraw_of_member_account = overdraw

    def get_acceptable_relative_account_deviation(self) -> int:
        return self.acceptable_relative_account_deviation

    def set_acceptable_relative_account_deviation(self, threshold: int) -> None:
        self.acceptable_relative_account_deviation = threshold
