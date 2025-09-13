from datetime import UTC, datetime


class FakeDatetimeFormatter:
    def format_datetime(
        self,
        date: datetime,
        fmt: str | None = None,
    ) -> str:
        if date.tzinfo is None:
            date = date.replace(tzinfo=UTC)
        date = date.astimezone(UTC)
        if fmt is None:
            fmt = "%d.%m.%Y %H:%M"
        return date.strftime(fmt)
