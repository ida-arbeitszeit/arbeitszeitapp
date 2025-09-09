from datetime import UTC, datetime
from typing import Optional
from zoneinfo import ZoneInfo

from arbeitszeit.datetime_service import DatetimeService


class RealtimeDatetimeService(DatetimeService):
    def now(self) -> datetime:
        return datetime.now(UTC)

    def format_datetime(
        self,
        date: datetime,
        zone: Optional[str] = None,
        fmt: Optional[str] = None,
    ) -> str:
        if zone is not None:
            date = date.astimezone(ZoneInfo(zone))
        if fmt is None:
            fmt = "%d.%m.%Y %H:%M"
        return date.strftime(fmt)
