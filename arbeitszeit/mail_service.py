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
