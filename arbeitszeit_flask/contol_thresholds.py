from flask import current_app


class ControlThresholdsFlask:
    def get_allowed_overdraw_of_member_account(self) -> int:
        return int(current_app.config["ALLOWED_OVERDRAW_MEMBER"])
