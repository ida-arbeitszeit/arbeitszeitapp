from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import Optional


class DatetimeService(ABC):
    @abstractmethod
    def today(self) -> date:
        pass

    @abstractmethod
    def now(self) -> datetime:
        pass

    @abstractmethod
    def format_datetime(
        self,
        date: datetime,
        zone: Optional[str] = ...,
        fmt: Optional[str] = ...,
    ) -> str:
        pass
