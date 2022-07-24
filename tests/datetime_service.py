from datetime import date, datetime, timedelta
from typing import Optional

from dateutil import tz
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

    def today(self) -> date:
        return (
            date(self.frozen_time.year, self.frozen_time.month, self.frozen_time.day)
            if self.frozen_time
            else date.today()
        )

    def format_datetime(
        self,
        date: datetime,
        zone: Optional[str] = None,
        fmt: Optional[str] = None,
    ) -> str:
        if zone is not None:
            date = date.astimezone(tz.gettz(zone))
        if fmt is None:
            fmt = "%d.%m.%Y %H:%M"
        return date.strftime(fmt)

    def now_minus_one_day(self) -> datetime:
        return self.now() - timedelta(days=1)

    def now_minus_20_hours(self) -> datetime:
        return self.now() - timedelta(hours=20)

    def now_minus_25_hours(self) -> datetime:
        return self.now() - timedelta(hours=25)

    def now_minus_two_days(self) -> datetime:
        return self.now() - timedelta(days=2)

    def now_minus_ten_days(self) -> datetime:
        return self.now() - timedelta(days=10)

    def now_plus_one_day(self) -> datetime:
        return self.now() + timedelta(days=1)
