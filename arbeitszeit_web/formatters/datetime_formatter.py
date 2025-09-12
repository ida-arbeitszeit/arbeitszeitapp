from datetime import datetime
from typing import Protocol


class DatetimeFormatter(Protocol):
    def format_datetime(
        self,
        date: datetime,
        fmt: str | None = ...,
    ) -> str: ...
