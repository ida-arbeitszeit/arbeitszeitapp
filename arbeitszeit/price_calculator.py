from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, List

from arbeitszeit import records
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class PriceCalculator:
    database_gateway: DatabaseGateway
    datetime_service: DatetimeService

    def calculate_cooperative_price(self, plan: records.Plan) -> Decimal:
        now = self.datetime_service.now()
        if plan.is_public_service:
            return Decimal(0)
        if plan.is_expired_as_of(now):
            return self.calculate_individual_price(plan)
        plans = list(
            self.database_gateway.get_plans()
            .that_are_in_same_cooperation_as(plan.id)
            .that_will_expire_after(now)
        )
        if not plans:
            return self.calculate_individual_price(plan)
        elif len(plans) == 1:
            return self.calculate_individual_price(plans[0])
        else:
            return self._calculate_coop_price(plans)

    def calculate_individual_price(self, plan: records.Plan) -> Decimal:
        return calculate_individual_price(plan)

    def _calculate_coop_price(self, plans: List[records.Plan]) -> Decimal:
        assert not any(plan.is_public_service for plan in plans)
        return calculate_average_costs([p.to_summary() for p in plans])


def calculate_individual_price(plan: records.Plan) -> Decimal:
    return plan.production_costs.total_cost() / plan.prd_amount


def calculate_average_costs(plans: Iterable[records.PlanSummary]) -> Decimal:
    cost_by_time = Decimal(0)
    amount_by_time = Decimal(0)
    for plan in plans:
        cost_by_time += plan.production_costs / Decimal(plan.duration_in_days)
        amount_by_time += Decimal(plan.amount) / Decimal(plan.duration_in_days)
    if not amount_by_time:
        return Decimal(0)
    else:
        return cost_by_time / amount_by_time
