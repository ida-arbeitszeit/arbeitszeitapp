from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from arbeitszeit import records
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class PriceCalculator:
    database_gateway: DatabaseGateway
    datetime_service: DatetimeService

    def calculate_cooperative_price(self, plan: UUID) -> Decimal | None:
        """
        Returns None if plan is not part of a cooperation.
        """
        now = self.datetime_service.now()
        plans = list(
            self.database_gateway.get_plans()
            .that_are_in_same_cooperation_as(plan)
            .that_will_expire_after(now)
        )
        if not plans:
            return None
        assert not any(p.is_public_service for p in plans)
        if len(plans) == 1:
            # Plan passed as argument is the sole member of a cooperation
            return plans[0].price_per_unit()
        else:
            return self._calculate_average_costs(plans)

    def _calculate_average_costs(self, plans: list[records.Plan]) -> Decimal:
        assert plans
        return Decimal(sum(plan.cost_per_unit() for plan in plans)) / Decimal(
            len(plans)
        )
