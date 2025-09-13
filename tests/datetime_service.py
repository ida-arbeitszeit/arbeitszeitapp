from datetime import UTC, datetime, timedelta
from typing import Optional

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.injector import singleton


def datetime_utc(
    year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: int = 0
) -> datetime:
    return datetime(year, month, day, hour, minute, second, tzinfo=UTC)


def datetime_min_utc() -> datetime:
    return datetime.min.replace(tzinfo=UTC)


@singleton
class FakeDatetimeService(DatetimeService):
    def __init__(self) -> None:
        self.frozen_time: Optional[datetime] = None

    def freeze_time(self, timestamp: Optional[datetime] = None) -> None:
        self.frozen_time = timestamp if timestamp else datetime.min.replace(tzinfo=UTC)

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
        if self.frozen_time:
            return self.frozen_time
        return datetime.now(UTC)

    def now_minus(self, delta: timedelta) -> datetime:
        return self.now() - delta
