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

    def now_minus_two_days(self) -> datetime:
        return self.now() - timedelta(days=2)

    def now_minus_ten_days(self) -> datetime:
        return self.now() - timedelta(days=10)

    def past_plan_activation_date(self, timedelta_days: int = 1) -> datetime:
        if self.now().hour < self.time_of_synchronized_plan_activation:
            past_day = self.today() - timedelta(days=timedelta_days)
            past_date = datetime(
                past_day.year,
                past_day.month,
                past_day.day,
                hour=self.time_of_synchronized_plan_activation,
            )
        else:
            past_day = self.today() - timedelta(days=timedelta_days - 1)
            past_date = datetime(
                past_day.year,
                past_day.month,
                past_day.day,
                hour=self.time_of_synchronized_plan_activation,
            )
        return past_date
