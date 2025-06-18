from arbeitszeit.injector import singleton


@singleton
class ControlThresholdsTestImpl:
    def __init__(self) -> None:
        self.allowed_overdraw_of_member_account: int | None = None
        self.acceptable_relative_account_deviation: int = 33

    def get_allowed_overdraw_of_member_account(self) -> int | None:
        return self.allowed_overdraw_of_member_account

    def set_allowed_overdraw_of_member_account(self, overdraw: int | None) -> None:
        self.allowed_overdraw_of_member_account = overdraw

    def get_acceptable_relative_account_deviation(self) -> int:
        return self.acceptable_relative_account_deviation

    def set_acceptable_relative_account_deviation(self, threshold: int) -> None:
        self.acceptable_relative_account_deviation = threshold
