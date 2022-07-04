from flask import current_app


class ControlThresholdsFlask:
    def get_allowed_overdraw_of_member_account(self) -> int:
        return int(current_app.config["ALLOWED_OVERDRAW_MEMBER"])

    def get_acceptable_relative_account_deviation(self) -> int:
        return int(current_app.config["ACCEPTABLE_RELATIVE_ACCOUNT_DEVIATION"])
