from datetime import date, datetime, timedelta

from arbeitszeit.datetime_service import DatetimeService


class RealtimeDatetimeService(DatetimeService):
    def now(self) -> datetime:
        return datetime.now()

    def today(self) -> date:
        return datetime.today()

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
