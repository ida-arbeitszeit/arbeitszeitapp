from dataclasses import dataclass
from decimal import Decimal
from typing import List

from arbeitszeit.decimal import decimal_sum
from arbeitszeit.entities import Plan


@dataclass
class PriceComponents:
    total_cost: Decimal
    amount: Decimal
    timeframe: Decimal
    is_public_service: bool


def calculate_price(cooperating_plans: List[Plan]) -> Decimal:
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
        return _calculate_individual_price(components)
    elif len(components) > 1:
        return _calculate_coop_price(components)
    else:
        raise AssertionError("No plans specified.")


def _calculate_individual_price(components: List[PriceComponents]) -> Decimal:
    component = components[0]
    return (
        component.total_cost / component.amount
        if not component.is_public_service
        else Decimal(0)
    )


def _calculate_coop_price(components: List[PriceComponents]) -> Decimal:

    for comp in components:
        assert (
            not comp.is_public_service
        ), "Public plans are not allowed in cooperations."

    coop_price = (
        decimal_sum([plan.total_cost / plan.timeframe for plan in components])
    ) / (decimal_sum([plan.amount / plan.timeframe for plan in components]) or 1)
    return coop_price
