from typing import Self

from flask import Flask
from flask_mail import Mail, Message

from .interface import EmailPlugin


class FlaskMailService(EmailPlugin):
    def __init__(self, mail: Mail):
        self.mail = mail

    @classmethod
    def initialize_plugin(cls, app: Flask) -> Self:
        mail = Mail()
        mail.init_app(app)
        return cls(mail)

    def send_message(
        self,
        subject: str,
        recipients: list[str],
        html: str,
        sender: str,
    ) -> None:
        message = Message(
            subject=subject,
            recipients=recipients,  # type: ignore[arg-type]
            html=html,
            sender=sender,
        )
        self.mail.send(message)
