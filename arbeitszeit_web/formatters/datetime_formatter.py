from datetime import datetime
from typing import Protocol


class DatetimeFormatter(Protocol):
    def format_datetime(
        self,
        date: datetime,
        zone: str | None = ...,
        fmt: str | None = ...,
    ) -> str: ...
