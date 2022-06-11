class ControlThresholdsTestImpl:
    allowed_overdraw_of_member_account: int = 0

    def get_allowed_overdraw_of_member_account(self) -> int:
        return self.allowed_overdraw_of_member_account

    def set_allowed_overdraw_of_member_account(self, overdraw: int) -> None:
        self.allowed_overdraw_of_member_account = overdraw
