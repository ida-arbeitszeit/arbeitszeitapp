from dataclasses import dataclass
from datetime import UTC, datetime, tzinfo
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from arbeitszeit.injector import singleton
from arbeitszeit_web.formatters.datetime_formatter import TimezoneConfiguration


@dataclass
class FakeDatetimeFormatter:
    timezone_config: TimezoneConfiguration

    def format_datetime(
        self,
        date: datetime,
        fmt: str | None = None,
    ) -> str:
        user_timezone = self.timezone_config.get_timezone_of_current_user()
        if date.tzinfo is None:
            date = date.replace(tzinfo=user_timezone)
        date = date.astimezone(user_timezone)
        if fmt is None:
            fmt = "%d.%m.%Y %H:%M"
        return date.strftime(fmt)


@singleton
class FakeTimezoneConfiguration:
    def __init__(self) -> None:
        self._tz: tzinfo = UTC

    def get_timezone_of_current_user(self) -> tzinfo:
        return self._tz

    def set_timezone_of_current_user(self, tz: str) -> None:
        try:
            zone_info = ZoneInfo(tz)
        except (ZoneInfoNotFoundError, TypeError):
            self._tz = UTC
        else:
            self._tz = zone_info
