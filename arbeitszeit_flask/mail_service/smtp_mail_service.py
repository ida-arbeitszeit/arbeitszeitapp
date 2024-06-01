from contextlib import contextmanager
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP_SSL
from typing import Generator, List, Self

from flask import Flask, current_app

from .interface import EmailPlugin


class SmtpMailService(EmailPlugin):
    @classmethod
    def initialize_plugin(cls, app: Flask) -> Self:
        return cls()

    def send_message(
        self,
        subject: str,
        recipients: List[str],
        html: str,
        sender: str,
    ) -> None:
        with self.create_smtp_connection() as smtp:
            message = MIMEMultipart()
            message["Subject"] = subject
            message["From"] = sender
            message.attach(MIMEText(html, "html"))
            for recipient in recipients:
                message["To"] = recipient
                smtp.send_message(message)

    @classmethod
    @contextmanager
    def create_smtp_connection(cls) -> Generator[SMTP_SSL, None, None]:
        server = current_app.config.get("MAIL_SERVER", "localhost")
        port = current_app.config.get("MAIL_PORT", "0")
        smtp = SMTP_SSL(server, port=port)
        smtp.ehlo()
        username = current_app.config.get("MAIL_USERNAME", "")
        password = current_app.config.get("MAIL_PASSWORD", "")
        smtp.login(username, password)
        yield smtp
        smtp.quit()
