from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService


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

    def unwrap_invitation_token(self, token: str) -> Optional[str]:
        return self.confirm_token(token, 10000000)

    def unwrap_confirmation_token(self, token: str) -> Optional[str]:
        return self.confirm_token(token, 10000000)


@dataclass
class DeliveredToken:
    token: str
    user: UUID


class TokenDeliveryService:
    def __init__(self) -> None:
        self.presented_member_tokens: List[DeliveredToken] = []
        self.presented_company_tokens: List[DeliveredToken] = []

    def show_member_registration_message(self, member: UUID, token: str) -> None:
        self.presented_member_tokens.append(DeliveredToken(user=member, token=token))

    def show_company_registration_message(self, company: UUID, token: str) -> None:
        self.presented_company_tokens.append(DeliveredToken(user=company, token=token))

    def get_deliviered_member_token(self, member: UUID) -> Optional[str]:
        for delivered_token in reversed(self.presented_member_tokens):
            if delivered_token.user == member:
                return delivered_token.token
        return None
