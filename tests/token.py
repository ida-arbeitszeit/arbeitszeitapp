from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.token import ConfirmationEmail


@dataclass
class FakeTokenService:
    datetime_service: DatetimeService

    def generate_token(self, input: str) -> str:
        timestamp = self.datetime_service.now().timestamp()
        return f"token_{timestamp}_{input}"

    def confirm_token(self, token: str, max_age_in_sec: int) -> Optional[str]:
        try:
            prefix, timestamp, text = tuple(token.split("_", 2))
        except ValueError:
            return None
        now = self.datetime_service.now().timestamp()
        time_passed = now - float(timestamp)
        if (prefix == "token") and (time_passed < max_age_in_sec):
            return text
        else:
            raise Exception()


class TokenDeliveryService:
    def __init__(self) -> None:
        self.delivered_tokens: List[ConfirmationEmail] = []
        self.presented_member_tokens: List[Tuple[UUID, str]] = []
        self.presented_company_tokens: List[Tuple[UUID, str]] = []

    def deliver_confirmation_token(self, email: ConfirmationEmail) -> None:
        self.delivered_tokens.append(email)

    def show_member_registration_message(self, member: UUID, token: str) -> None:
        self.presented_member_tokens.append((member, token))

    def show_company_registration_message(self, company: UUID, token: str) -> None:
        self.presented_company_tokens.append((company, token))
