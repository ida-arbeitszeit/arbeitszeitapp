from datetime import UTC, datetime, tzinfo
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from flask import current_app

from arbeitszeit.datetime_service import DatetimeService


class RealtimeDatetimeService(DatetimeService):
    def now(self) -> datetime:
        return datetime.now(UTC)


class FlaskDatetimeFormatter:
    def format_datetime(
        self,
        date: datetime,
        fmt: str | None = None,
    ) -> str:
        date = date.astimezone(self.get_timezone())
        if fmt is None:
            fmt = "%d.%m.%Y %H:%M"
        return date.strftime(fmt)

    def get_timezone(self) -> tzinfo:
        timezone = current_app.config.get("DEFAULT_USER_TIMEZONE", "UTC")
        try:
            zone_info = ZoneInfo(timezone)
        except (ZoneInfoNotFoundError, TypeError):
            return UTC
        return zone_info
