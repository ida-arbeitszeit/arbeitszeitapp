from typing import List

from flask import current_app, render_template, url_for
from flask_mail import Message

from arbeitszeit_flask.extensions import mail
from arbeitszeit_web.email import MailService


class FlaskEmailConfiguration:
    def get_sender_address(self) -> str:
        return current_app.config["MAIL_DEFAULT_SENDER"]


def get_mail_service() -> MailService:
    if current_app.config.get("MAIL_BACKEND") == "flask_mail":
        return FlaskMailService()
    else:
        return DebugMailService()


class DebugMailService:
    def send_message(
        self,
        subject: str,
        recipients: List[str],
        html: str,
        sender: str,
    ) -> None:
        print("Email would be sent:")
        print(f"recipients: {' '.join(recipients)}")
        print(f"subject: {subject}")
        print(f"sender: {sender}")
        print(f"content: {html}")

    def create_confirmation_html(
        self, template_name: str, endpoint: str, token: str
    ) -> str:
        confirm_url = url_for(endpoint=endpoint, token=token, _external=True)
        return render_template(template_name, confirm_url=confirm_url)


class FlaskMailService:
    def send_message(
        self,
        subject: str,
        recipients: List[str],
        html: str,
        sender: str,
    ) -> None:
        msg = Message(subject=subject, recipients=recipients, html=html, sender=sender)
        mail.send(msg)
