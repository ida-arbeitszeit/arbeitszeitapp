from typing import Self

from flask import Flask
from flask_mail import Message

from arbeitszeit_flask.extensions import mail

from .interface import EmailPlugin


class FlaskMailService(EmailPlugin):
    @classmethod
    def initialize_plugin(cls, app: Flask) -> Self:
        mail.init_app(app)
        return cls()

    def send_message(
        self,
        subject: str,
        recipients: list[str],
        html: str,
        sender: str,
    ) -> None:
        msg = Message(subject=subject, recipients=recipients, html=html, sender=sender)
        mail.send(msg)
