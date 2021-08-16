from datetime import date, datetime, timedelta

from injector import singleton

from arbeitszeit.datetime_service import DatetimeService


@singleton
class FakeDatetimeService(DatetimeService):
    def __init__(self):
        super().__init__()
        self.frozen_time = None
        self.frozen_date = None

    def freeze_time(self, timestamp: datetime):
        self.frozen_time = timestamp

    def freeze_date(self, datestamp: date):
        self.frozen_date = datestamp

    def now(self) -> datetime:
        return self.frozen_time if self.frozen_time else datetime.now()

    def today(self) -> date:
        return self.frozen_date if self.frozen_date else date.today()

    def now_minus_one_day(self) -> datetime:
        return self.now() - timedelta(days=1)

    def now_minus_two_days(self) -> datetime:
        return self.now() - timedelta(days=2)

    def past_plan_activation_date(self, timedelta_days: int = 1) -> datetime:
        if self.now().hour < self.time_of_plan_activation:
            past_day = self.today() - timedelta(days=timedelta_days)
            past_date = datetime(
                past_day.year,
                past_day.month,
                past_day.day,
                hour=self.time_of_plan_activation,
            )
        else:
            past_day = self.today() - timedelta(days=timedelta_days - 1)
            past_date = datetime(
                past_day.year,
                past_day.month,
                past_day.day,
                hour=self.time_of_plan_activation,
            )
        return past_date
