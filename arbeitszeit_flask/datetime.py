from datetime import date, datetime

from arbeitszeit.datetime_service import DatetimeService


class RealtimeDatetimeService(DatetimeService):
    def now(self) -> datetime:
        return datetime.now()

    def today(self) -> date:
        return datetime.today().date()
