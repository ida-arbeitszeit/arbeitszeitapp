from datetime import datetime, timedelta

from injector import singleton

from arbeitszeit.datetime_service import DatetimeService


@singleton
class FakeDatetimeService(DatetimeService):
    def __init__(self):
        self.frozen_time = None

    def freeze_time(self, timestamp: datetime):
        self.frozen_time = timestamp

    def now(self) -> datetime:
        return self.frozen_time if self.frozen_time else datetime.now()

    def now_minus_one_day(self) -> datetime:
        return self.now() - timedelta(days=1)

    def now_minus_two_days(self) -> datetime:
        return self.now() - timedelta(days=2)
