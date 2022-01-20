from typing import List

from flask import current_app, render_template, url_for
from flask_mail import Message

from arbeitszeit.errors import CannotSendEmail
from arbeitszeit.mail_service import MailService
from arbeitszeit_flask.extensions import mail


def get_mail_service():
    if current_app.config.get("MAIL_BACKEND") == "flask_mail":
        return FlaskMailService()
    else:
        return DebugMailService()


class DebugMailService(MailService):
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


class FlaskMailService(MailService):
    def send_message(
        self,
        subject: str,
        recipients: List[str],
        html: str,
        sender: str,
    ) -> None:
        msg = Message(subject=subject, recipients=recipients, html=html, sender=sender)
        try:
            mail.send(msg)
        except Exception:
            raise CannotSendEmail

    def create_confirmation_html(
        self, template_name: str, endpoint: str, token: str
    ) -> str:
        confirm_url = url_for(endpoint=endpoint, token=token, _external=True)
        return render_template(template_name, confirm_url=confirm_url)
