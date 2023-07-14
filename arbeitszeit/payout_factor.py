from dataclasses import dataclass
from decimal import Decimal

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.decimal import decimal_sum
from arbeitszeit.entities import PayoutFactor, ProductionCosts
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class PayoutFactorService:
    datetime_service: DatetimeService
    database_gateway: DatabaseGateway

    def calculate_payout_factor(self) -> Decimal:
        now = self.datetime_service.now()
        active_plans = (
            self.database_gateway.get_plans()
            .that_will_expire_after(now)
            .that_were_activated_before(now)
        )
        # payout factor = (A − ( P o + R o )) / (A + A o)
        productive_plans = active_plans.that_are_productive()
        public_plans = active_plans.that_are_public()
        if not public_plans:
            return Decimal(1)
        # A o, P o, R o
        public_costs_per_day: ProductionCosts = sum(
            (p.production_costs / p.timeframe for p in public_plans),
            start=ProductionCosts(Decimal(0), Decimal(0), Decimal(0)),
        )
        # A
        sum_of_productive_work_per_day = decimal_sum(
            p.production_costs.labour_cost / p.timeframe for p in productive_plans
        )
        numerator = sum_of_productive_work_per_day - (
            public_costs_per_day.means_cost + public_costs_per_day.resource_cost
        )
        denominator = (
            sum_of_productive_work_per_day + public_costs_per_day.labour_cost
        ) or 1
        # Payout factor
        payout_factor = numerator / denominator
        return Decimal(payout_factor)

    def store_payout_factor(self, payout_factor: Decimal) -> PayoutFactor:
        return self.database_gateway.create_payout_factor(
            self.datetime_service.now(), payout_factor
        )

    def get_current_payout_factor(self) -> PayoutFactor:
        return self.store_payout_factor(self.calculate_payout_factor())
