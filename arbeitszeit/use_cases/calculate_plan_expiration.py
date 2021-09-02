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

    def __call__(self) -> None:
        for plan in self.plan_repository.all_active_plans():
            self._calculate_plan_expiration(plan)

    def _calculate_plan_expiration(self, plan: Plan) -> None:
        assert plan.is_active, "Plan is not active!"
        assert plan.activation_date, "Plan has no activation date!"
        activation_day = datetime.date(
            plan.activation_date.year,
            plan.activation_date.month,
            plan.activation_date.day,
        )
        expiration_day = activation_day + datetime.timedelta(days=int(plan.timeframe))
        expiration_time = datetime.datetime(
            expiration_day.year,
            expiration_day.month,
            expiration_day.day,
            self.datetime_service.time_of_synchronized_plan_activation,
        )
        days_relative = (
            0
            if expiration_day == self.datetime_service.today()
            else (expiration_day - activation_day).days
        )
        self.plan_repository.set_expiration_relative(plan, days_relative)
        self.plan_repository.set_expiration_date(plan, expiration_time)

        assert plan.expiration_date
        if self.datetime_service.now() > plan.expiration_date:
            self.plan_repository.set_plan_as_expired(plan)
