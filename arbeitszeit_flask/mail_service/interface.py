from abc import ABC, abstractmethod
from typing import Self

from flask import Flask


class EmailPlugin(ABC):
    @classmethod
    @abstractmethod
    def initialize_plugin(cls, app: Flask) -> Self:
        pass

    @abstractmethod
    def send_message(
        self,
        subject: str,
        recipients: list[str],
        html: str,
        sender: str,
    ) -> None:
        pass
