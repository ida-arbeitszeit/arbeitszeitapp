from datetime import datetime
from typing import Optional, Union

from dateutil import parser, tz


def format_datetime(
    date: Union[str, datetime], zone: Optional[str] = None, fmt: Optional[str] = None
):
    if isinstance(date, str):
        date = parser.parse(date)
    if zone is not None:
        date = date.astimezone(tz.gettz(zone))
    if fmt is None:
        fmt = "%d.%m.%Y %H:%M"
    return date.strftime(fmt)
