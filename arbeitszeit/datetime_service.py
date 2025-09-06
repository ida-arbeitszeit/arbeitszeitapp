from datetime import datetime
from typing import Protocol


class DatetimeService(Protocol):
    def now(self) -> datetime: ...
