from datetime import datetime, timedelta


class DatetimeService:
    def now(self) -> datetime:
        return datetime.now()

    def yesterday(self) -> datetime:
        return datetime.now() - timedelta(days=1)
