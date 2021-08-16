import datetime
from dataclasses import dataclass

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Plan
from arbeitszeit.repositories import PlanRepository


@inject
@dataclass
class CalculatePlanExpirationAndCheckIfExpired:
    datetime_service: DatetimeService
    plan_repository: PlanRepository

    def __call__(self, plan: Plan) -> None:
        if not plan.is_active:
            raise (Exception("Plan is not active!"))
        else:
            activation_day = datetime.date(
                plan.activation_date.year,
                plan.activation_date.month,
                plan.activation_date.day,
            )
            expiration_day = activation_day + datetime.timedelta(
                days=int(plan.timeframe)
            )
            expiration_time = datetime.datetime(
                expiration_day.year,
                expiration_day.month,
                expiration_day.day,
                self.datetime_service.time_of_plan_activation,
            )
            days_relative = expiration_day - activation_day
            self.plan_repository.set_expiration_relative(plan, days_relative.days)
            self.plan_repository.set_expiration_date(plan, expiration_time)

            if self.datetime_service.now() > plan.expiration_date:
                self.plan_repository.set_plan_as_expired(plan)
