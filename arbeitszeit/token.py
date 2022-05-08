from dataclasses import dataclass
from typing import Optional, Protocol


class TokenService(Protocol):
    def generate_token(self, input: str) -> str:
        ...


class InvitationTokenValidator(Protocol):
    def unwrap_invitation_token(self, token: str) -> Optional[str]:
        ...


@dataclass
class ConfirmationEmail:
    token: str
    email: str


class TokenDeliverer(Protocol):
    def deliver_confirmation_token(self, email: ConfirmationEmail) -> None:
        ...
