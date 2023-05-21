from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import List, Optional

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.injector import singleton


@singleton
@dataclass
class FakeTokenService:
    datetime_service: DatetimeService

    def generate_token(self, input: str) -> str:
        timestamp = self.datetime_service.now().timestamp()
        return f"token_{timestamp}_{input}"

    def confirm_token(self, token: str, max_age: timedelta) -> Optional[str]:
        try:
            prefix, timestamp, text = tuple(token.split("_", 2))
        except ValueError:
            return None
        now = self.datetime_service.now().timestamp()
        time_passed = now - float(timestamp)
        if (prefix == "token") and (time_passed < max_age.total_seconds()):
            return text
        else:
            return None


@dataclass
class DeliveredToken:
    email_address: str


@singleton
class TokenDeliveryService:
    def __init__(self) -> None:
        self.presented_member_tokens: List[DeliveredToken] = []
        self.presented_company_tokens: List[DeliveredToken] = []

    def show_member_registration_message(self, email_address: str) -> None:
        self.presented_member_tokens.append(DeliveredToken(email_address=email_address))

    def show_company_registration_message(self, email_address: str) -> None:
        self.presented_company_tokens.append(
            DeliveredToken(email_address=email_address)
        )

    def has_token_delivered_for(self, email_address: str) -> bool:
        for delivered_token in reversed(self.presented_member_tokens):
            if delivered_token.email_address == email_address:
                return True
        return False
