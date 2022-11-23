from dataclasses import dataclass
from typing import List, Optional, Set
from uuid import UUID

from injector import singleton


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


@singleton
class FakeAddressBook:
    def __init__(self) -> None:
        self._blacklisted_users: Set[UUID] = set()

    def blacklist_user(self, user: UUID) -> None:
        self._blacklisted_users.add(user)

    def get_user_email_address(self, user: UUID) -> Optional[str]:
        if user in self._blacklisted_users:
            return None
        return f"{user}@test.test"


class FakeEmailConfiguration:
    def get_sender_address(self) -> str:
        return "test@test.test"
