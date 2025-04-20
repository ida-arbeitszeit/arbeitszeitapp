from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Iterable

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.records import Plan
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class PayoutFactorService:
    datetime_service: DatetimeService
    database_gateway: DatabaseGateway

    def calculate_payout_factor(self, timestamp: datetime) -> Decimal:
        active_plans = (
            self.database_gateway.get_plans()
            .that_will_expire_after(timestamp)
            .that_were_approved_before(timestamp)
        )
        return calculate_payout_factor(active_plans)

    def get_current_payout_factor(self) -> Decimal:
        now = self.datetime_service.now()
        return self.calculate_payout_factor(now)


def calculate_payout_factor(plans: Iterable[Plan]) -> Decimal:
    # payout factor = (L − ( P_o + R_o )) / (L + L_o)
    l: Decimal = Decimal(0)
    l_o: Decimal = Decimal(0)
    p_o_and_r_o = Decimal(0)
    for plan in plans:
        costs = plan.production_costs
        if plan.is_public_service:
            l_o += costs.labour_cost
            p_o_and_r_o += costs.means_cost + costs.resource_cost
        else:
            l += costs.labour_cost
    if l + l_o:
        return (l - p_o_and_r_o) / (l + l_o)
    else:
        return Decimal(1)
