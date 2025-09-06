from datetime import datetime, timedelta, timezone
from typing import Optional

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

    def format_datetime(
        self,
        date: datetime,
        zone: Optional[str] = None,
        fmt: Optional[str] = None,
    ) -> str:
        if date.tzinfo is None:
            date = date.replace(tzinfo=timezone.utc)
        if zone is not None:
            date = date.astimezone(tz.gettz(zone))
        if fmt is None:
            fmt = "%d.%m.%Y %H:%M"
        return date.strftime(fmt)

    def now_minus(self, delta: timedelta) -> datetime:
        return self.now() - delta
