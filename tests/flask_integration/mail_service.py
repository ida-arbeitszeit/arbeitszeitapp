from contextlib import contextmanager
from dataclasses import dataclass
from typing import Generator, Self

from flask import Flask

from arbeitszeit_flask.mail_service.interface import EmailPlugin


@dataclass
class DeliveredEmail:
    subject: str
    recipients: list[str]
    sender: str
    html: str


class MockEmailService(EmailPlugin):
    def __init__(self) -> None:
        self._outbox: list[DeliveredEmail] | None = None

    @classmethod
    def initialize_plugin(cls, app: Flask) -> Self:
        return cls()

    def send_message(
        self,
        subject: str,
        recipients: list[str],
        html: str,
        sender: str,
    ) -> None:
        if self._outbox is not None:
            self._outbox.append(
                DeliveredEmail(
                    subject=subject,
                    recipients=recipients,
                    sender=sender,
                    html=html,
                )
            )

    @contextmanager
    def record_messages(self) -> Generator[list[DeliveredEmail], None, None]:
        old_outbox = self._outbox
        self._outbox = []
        yield self._outbox
        self._outbox = old_outbox
