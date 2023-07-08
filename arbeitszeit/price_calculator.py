from dataclasses import dataclass
from decimal import Decimal
from typing import List

from arbeitszeit.decimal import decimal_sum
from arbeitszeit.entities import Plan
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class PriceCalculator:
    database_gateway: DatabaseGateway

    def calculate_cooperative_price(self, plan: Plan) -> Decimal:
        if plan.is_public_service:
            return Decimal(0)
        plans = list(
            self.database_gateway.get_plans().that_are_in_same_cooperation_as(plan.id)
        )
        assert plans
        if len(plans) == 1:
            return self.calculate_individual_price(plans[0])
        else:
            return self._calculate_coop_price(plans)

    def calculate_individual_price(self, plan: Plan) -> Decimal:
        if plan.is_public_service:
            return Decimal(0)
        return plan.production_costs.total_cost() / plan.prd_amount

    def _calculate_coop_price(self, plans: List[Plan]) -> Decimal:
        assert not any(plan.is_public_service for plan in plans)
        coop_price = (
            decimal_sum(
                plan.production_costs.total_cost() / plan.timeframe for plan in plans
            )
        ) / (
            decimal_sum(Decimal(plan.prd_amount) / plan.timeframe for plan in plans)
            or 1
        )
        return coop_price
