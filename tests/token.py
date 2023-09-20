from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Optional

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
