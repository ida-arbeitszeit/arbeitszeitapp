from abc import ABC, abstractmethod
from datetime import date, datetime


class DatetimeService(ABC):
    @abstractmethod
    def today(self) -> date:
        pass

    @abstractmethod
    def now(self) -> datetime:
        pass
