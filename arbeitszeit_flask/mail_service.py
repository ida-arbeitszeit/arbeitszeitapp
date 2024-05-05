from contextlib import contextmanager
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP_SSL
from typing import Generator, List

from flask import current_app, render_template, url_for
from flask_mail import Message

from arbeitszeit_flask.extensions import mail
from arbeitszeit_web.email import MailService


class FlaskEmailConfiguration:
    def get_sender_address(self) -> str:
        return current_app.config["MAIL_DEFAULT_SENDER"]

    def get_admin_email_address(self) -> str | None:
        return current_app.config.get("MAIL_ADMIN")


def get_mail_service() -> MailService:
    match current_app.config.get("MAIL_BACKEND"):
        case "flask_mail":
            return FlaskMailService()
        case "smtplib_ssl":
            return SmtpMailService()
        case _:
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


@dataclass
class SmtpMailService:
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
