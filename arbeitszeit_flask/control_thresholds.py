from flask import current_app


class ControlThresholdsFlask:
    def get_allowed_overdraw_of_member_account(self) -> int | None:
        value = current_app.config["ALLOWED_OVERDRAW_MEMBER"]
        return None if value == "unlimited" else int(value)

    def get_acceptable_relative_account_deviation(self) -> int:
        return int(current_app.config["ACCEPTABLE_RELATIVE_ACCOUNT_DEVIATION"])
