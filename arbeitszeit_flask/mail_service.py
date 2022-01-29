from dataclasses import dataclass
from typing import List, Protocol

from flask import current_app, render_template, url_for
from flask_mail import Message

from arbeitszeit.errors import CannotSendEmail
from arbeitszeit.token import ConfirmationEmail
from arbeitszeit_flask.extensions import mail
from arbeitszeit_web.presenters.send_confirmation_email_presenter import (
    SendConfirmationEmailPresenter,
)


class FlaskEmailConfiguration:
    def get_sender_address(self) -> str:
        return current_app.config["MAIL_DEFAULT_SENDER"]


class MailService(Protocol):
    def send_message(
        self,
        subject: str,
        recipients: List[str],
        html: str,
        sender: str,
    ) -> None:
        ...


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
        try:
            mail.send(msg)
        except Exception:
            raise CannotSendEmail


@dataclass
class FlaskTokenDeliverer:
    presenter: SendConfirmationEmailPresenter
    mail_service: MailService

    def deliver_confirmation_token(self, email: ConfirmationEmail) -> None:
        view_model = self.presenter.render_confirmation_email(email)
        html = render_template("activate.html", confirm_url=view_model.confirmation_url)
        self.mail_service.send_message(
            subject=view_model.subject,
            recipients=view_model.recipients,
            html=html,
            sender=view_model.sender,
        )
