from abc import ABC, abstractmethod
from typing import List


class MailService(ABC):
    @abstractmethod
    def send_message(
        self,
        subject: str,
        recipients: List[str],
        html: str,
        sender: str,
    ) -> None:
        ...

    @abstractmethod
    def create_confirmation_html(
        self, template_name: str, endpoint: str, token: str
    ) -> str:
        ...
