from datetime import datetime
from typing import Optional

from dateutil import tz

from arbeitszeit.datetime_service import DatetimeService


class RealtimeDatetimeService(DatetimeService):
    def now(self) -> datetime:
        return datetime.now()

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
