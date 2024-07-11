from datetime import date, datetime, timedelta
from typing import Optional

import pytz
from dateutil import tz

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.injector import singleton


@singleton
class FakeDatetimeService(DatetimeService):
    def __init__(self) -> None:
        self.frozen_time: Optional[datetime] = None

    def freeze_time(self, timestamp: Optional[datetime] = None) -> None:
        self.frozen_time = timestamp if timestamp else datetime.min

    def unfreeze_time(self) -> None:
        self.frozen_time = None

    def advance_time(self, dt: Optional[timedelta] = None) -> datetime:
        assert self.frozen_time
        if dt is not None:
            assert dt > timedelta(0)
            self.frozen_time += dt
        else:
            self.frozen_time += timedelta(seconds=1)
        return self.frozen_time

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
        if date.tzinfo is None:
            date = date.replace(tzinfo=pytz.UTC)
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
