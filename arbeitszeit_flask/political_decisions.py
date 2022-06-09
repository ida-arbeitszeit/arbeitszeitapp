from flask import current_app


class PoliticalDecisionsFlask:
    def get_allowed_overdraw_of_member_account(self) -> int:
        return int(current_app.config["ALLOWED_OVERDRAW_MEMBER"])

    def set_allowed_overdraw_of_member_account(self, overdraw: int) -> None:
        ...
