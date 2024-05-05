from flask import current_app


class FlaskEmailConfiguration:
    def get_sender_address(self) -> str:
        return current_app.config["MAIL_DEFAULT_SENDER"]

    def get_admin_email_address(self) -> str | None:
        return current_app.config.get("MAIL_ADMIN")
