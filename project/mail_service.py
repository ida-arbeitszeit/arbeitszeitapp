from typing import List

from flask import render_template, url_for
from flask_mail import Message
from injector import singleton

from arbeitszeit.errors import CannotSendEmail
from arbeitszeit.mail_service import MailService
from project.extensions import mail


@singleton
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
