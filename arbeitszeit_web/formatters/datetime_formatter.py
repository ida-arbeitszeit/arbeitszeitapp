from datetime import datetime, tzinfo
from typing import Protocol


class DatetimeFormatter(Protocol):
    def format_datetime(
        self,
        date: datetime,
        fmt: str | None = ...,
    ) -> str: ...


class TimezoneConfiguration(Protocol):
    def get_timezone_of_current_user(self) -> tzinfo: ...
