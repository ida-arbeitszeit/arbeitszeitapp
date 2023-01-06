from dataclasses import dataclass
from decimal import Decimal
from typing import List

from injector import inject

from arbeitszeit.decimal import decimal_sum
from arbeitszeit.entities import Plan
from arbeitszeit.repositories import PlanRepository


@dataclass
class PriceComponents:
    total_cost: Decimal
    amount: Decimal
    timeframe: Decimal
    is_public_service: bool


@inject
@dataclass
class PriceCalculator:
    plan_repository: PlanRepository

    def calculate_cooperative_price(self, plan: Plan) -> Decimal:
        if plan.is_public_service:
            return Decimal(0)
        return self._calculate_price(
            list(
                self.plan_repository.get_plans().that_are_in_same_cooperation_as(
                    plan.id
                )
            )
        )

    def calculate_individual_price(self, plan: Plan) -> Decimal:
        if plan.is_public_service:
            return Decimal(0)
        return plan.production_costs.total_cost() / plan.prd_amount

    def _calculate_price(self, cooperating_plans: List[Plan]) -> Decimal:
        components = [
            PriceComponents(
                plan.production_costs.total_cost(),
                Decimal(plan.prd_amount),
                Decimal(plan.timeframe),
                plan.is_public_service,
            )
            for plan in cooperating_plans
        ]

        if len(components) == 1:
            return self._calculate_individual_price(components)
        elif len(components) > 1:
            return self._calculate_coop_price(components)
        else:
            raise AssertionError("No plans specified.")

    def _calculate_individual_price(self, components: List[PriceComponents]) -> Decimal:
        component = components[0]
        return (
            component.total_cost / component.amount
            if not component.is_public_service
            else Decimal(0)
        )

    def _calculate_coop_price(self, components: List[PriceComponents]) -> Decimal:

        for comp in components:
            assert (
                not comp.is_public_service
            ), "Public plans are not allowed in cooperations."

        coop_price = (
            decimal_sum([plan.total_cost / plan.timeframe for plan in components])
        ) / (decimal_sum([plan.amount / plan.timeframe for plan in components]) or 1)
        return coop_price
