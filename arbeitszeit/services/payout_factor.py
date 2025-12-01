from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.records import Plan
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class PayoutFactorService:
    datetime_service: DatetimeService
    database_gateway: DatabaseGateway

    def calculate_current_payout_factor(self) -> Decimal:
        now = self.datetime_service.now()
        active_plans = (
            self.database_gateway.get_plans()
            .that_were_approved_before(now)
            .that_will_expire_after(now)
        )
        return self._calculate_payout_factor(active_plans)

    @classmethod
    def _calculate_payout_factor(cls, plans: Iterable[Plan]) -> Decimal:
        # payout factor or factor of individual consumption (FIC)
        # = (l − ( p_o + r_o )) / (l + l_o)
        # where:
        # l = labour in productive plans
        # l_o = labour in public plans
        # p_o = means of production in public plans
        # r_o = raw materials in public plans

        if not plans:
            return Decimal(1)

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
        total_labour = l + l_o

        if not total_labour:
            # prevent division by zero
            if p_o_and_r_o:
                return Decimal(0)
            return Decimal(1)

        possibly_negative_fic = (l - p_o_and_r_o) / total_labour
        return max(Decimal(0), possibly_negative_fic)
