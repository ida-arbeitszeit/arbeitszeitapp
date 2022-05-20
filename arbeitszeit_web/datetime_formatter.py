from datetime import datetime
from typing import Optional, Protocol, Union


class DatetimeFormatter(Protocol):
    def format_datetime(
        self,
        date: Union[str, datetime],
        zone: Optional[str] = ...,
        fmt: Optional[str] = ...,
    ) -> str:
        ...
