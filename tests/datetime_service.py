from datetime import date, datetime, timedelta

from injector import singleton

from arbeitszeit.datetime_service import DatetimeService


@singleton
class FakeDatetimeService(DatetimeService):
    def __init__(self):
        super().__init__()
        self.frozen_time = None

    def freeze_time(self, timestamp: datetime):
        self.frozen_time = timestamp

    def now(self) -> datetime:
        return self.frozen_time if self.frozen_time else datetime.now()

    def today(self) -> date:
        return (
            date(self.frozen_time.year, self.frozen_time.month, self.frozen_time.day)
            if self.frozen_time
            else date.today()
        )

    def now_minus_one_day(self) -> datetime:
        return self.now() - timedelta(days=1)

    def now_minus_20_hours(self) -> datetime:
        return self.now() - timedelta(hours=20)

    def now_minus_25_hours(self) -> datetime:
        return self.now() - timedelta(hours=25)

    def now_minus_two_days(self) -> datetime:
        return self.now() - timedelta(days=2)

    def now_minus_ten_days(self) -> datetime:
        return self.now() - timedelta(days=10)

    def now_plus_one_day(self) -> datetime:
        return self.now() + timedelta(days=1)
