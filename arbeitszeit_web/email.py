from typing import List, Protocol
from uuid import UUID


class EmailConfiguration(Protocol):
    def get_sender_address(self) -> str:
        ...


class MailService(Protocol):
    def send_message(
        self,
        subject: str,
        recipients: List[str],
        html: str,
        sender: str,
    ) -> None:
        ...


class UserAddressBook(Protocol):
    def get_user_email_address(self, user: UUID) -> str:
        ...
