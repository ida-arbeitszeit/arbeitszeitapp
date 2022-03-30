from __future__ import annotations

from typing import List, Tuple
from uuid import UUID

from arbeitszeit.token import ConfirmationEmail

from .datetime_service import FakeDatetimeService


class FakeTokenService:
    def generate_token(self, input: str) -> str:
        timestamp = FakeDatetimeService().now().timestamp()
        return f"token_{timestamp}_{input}"

    def confirm_token(self, token: str, max_age_in_sec: int) -> str:
        prefix, timestamp, text = tuple(token.split("_", 2))
        now = FakeDatetimeService().now().timestamp()
        time_passed = now - float(timestamp)
        if (prefix == "token") and (time_passed < max_age_in_sec):
            return text
        else:
            raise Exception()


class TokenDeliveryService:
    def __init__(self) -> None:
        self.delivered_tokens: List[ConfirmationEmail] = []
        self.presented_member_tokens: List[Tuple[UUID, str]] = []

    def deliver_confirmation_token(self, email: ConfirmationEmail) -> None:
        self.delivered_tokens.append(email)

    def show_member_registration_message(self, member: UUID, token: str) -> None:
        self.presented_member_tokens.append((member, token))
