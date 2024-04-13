from datetime import date, datetime
from typing import Protocol


class DatetimeService(Protocol):
    def today(self) -> date: ...

    def now(self) -> datetime: ...
