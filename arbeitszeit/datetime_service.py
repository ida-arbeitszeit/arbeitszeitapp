from abc import ABC, abstractmethod
from datetime import datetime


class DatetimeService(ABC):
    @abstractmethod
    def now(self) -> datetime:
        pass
