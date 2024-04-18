from typing import List, Protocol


class EmailConfiguration(Protocol):
    def get_sender_address(self) -> str: ...

    def get_admin_email_address(self) -> str | None: ...


class MailService(Protocol):
    def send_message(
        self,
        subject: str,
        recipients: List[str],
        html: str,
        sender: str,
    ) -> None: ...
