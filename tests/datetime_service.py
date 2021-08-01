from datetime import datetime, timedelta
from arbeitszeit.datetime_service import DatetimeService


class TestDatetimeService(DatetimeService):
    def now_minus_one_day(self) -> datetime:
        return datetime.now() - timedelta(days=1)

    def now_minus_two_days(self) -> datetime:
        return datetime.now() - timedelta(days=2)
