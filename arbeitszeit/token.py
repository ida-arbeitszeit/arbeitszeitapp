from dataclasses import dataclass
from typing import Protocol


class TokenService(Protocol):
    def generate_token(self, input: str) -> str:
        ...

    def confirm_token(self, token: str, max_age_in_sec: int) -> str:
        ...


@dataclass
class ConfirmationEmail:
    token: str
    email: str


class TokenDeliverer(Protocol):
    def deliver_confirmation_token(self, email: ConfirmationEmail) -> None:
        ...
