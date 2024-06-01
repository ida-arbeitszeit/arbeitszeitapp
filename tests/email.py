from dataclasses import dataclass
from typing import List

from arbeitszeit.injector import singleton


@dataclass
class Email:
    subject: str
    recipients: List[str]
    html: str
    sender: str


@singleton
class FakeEmailService:
    def __init__(self) -> None:
        self.sent_mails: List[Email] = []

    def send_message(
        self,
        subject: str,
        recipients: List[str],
        html: str,
        sender: str,
    ) -> None:
        self.sent_mails.append(
            Email(
                subject=subject,
                recipients=recipients,
                html=html,
                sender=sender,
            )
        )


@singleton
class FakeEmailConfiguration:
    def __init__(self) -> None:
        self._admin_email_address: str | None = None

    def set_admin_email_address(self, email_address: str) -> None:
        self._admin_email_address = email_address

    def get_sender_address(self) -> str:
        return "test@test.test"

    def get_admin_email_address(self) -> str | None:
        return self._admin_email_address
