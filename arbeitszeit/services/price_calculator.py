from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable

from arbeitszeit import records
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class PriceCalculator:
    database_gateway: DatabaseGateway
    datetime_service: DatetimeService

    def calculate_cooperative_price(self, plan: records.Plan) -> Decimal:
        now = self.datetime_service.now()
        plans = list(
            self.database_gateway.get_plans()
            .that_are_in_same_cooperation_as(plan.id)
            .that_will_expire_after(now)
        )
        if not plans:
            return plan.price_per_unit()
        elif len(plans) == 1:
            return plans[0].price_per_unit()
        else:
            return self._calculate_average_costs(plans)

    def _calculate_average_costs(self, plans: Iterable[records.Plan]) -> Decimal:
        if not isinstance(plans, list):
            plans = list(plans)
        assert not any(plan.is_public_service for plan in plans)
        if not plans:
            return Decimal(0)

        return sum(plan.cost_per_unit() for plan in plans) / len(plans)
