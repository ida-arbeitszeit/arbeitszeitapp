from typing import List

from flask_mail import Message
from injector import singleton

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
        mail.send(msg)
