from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID


@dataclass
class Email:
    subject: str
    recipients: List[str]
    html: str
    sender: str


class FakeEmailSender:
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


class FakeAddressBook:
    def get_user_email_address(self, user: UUID) -> Optional[str]:
        return f"{user}@test.test"


class FakeEmailConfiguration:
    def get_sender_address(self) -> str:
        return "test@test.test"


class RegistrationEmailTemplateImpl:
    def render_to_html(self, confirmation_url: str) -> str:
        return f"member confirmation mail {confirmation_url}"
