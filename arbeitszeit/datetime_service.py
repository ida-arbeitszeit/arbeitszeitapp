from abc import ABC, abstractmethod
from datetime import datetime


class DatetimeService(ABC):
    def __init__(self) -> None:
        self.time_of_plan_activation = 10

    @abstractmethod
    def now(self) -> datetime:
        pass

    @abstractmethod
    def past_plan_activation_date(self, timedelta_days: int = 1) -> datetime:
        pass
