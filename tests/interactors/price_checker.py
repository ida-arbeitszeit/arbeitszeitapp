from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from arbeitszeit.interactors.get_plan_details import GetPlanDetailsInteractor


@dataclass
class PriceChecker:
    get_plan_details: GetPlanDetailsInteractor

    def get_price_per_unit(self, plan: UUID) -> Decimal:
        request = GetPlanDetailsInteractor.Request(plan)
        response = self.get_plan_details.get_plan_details(request)
        assert response
        return response.plan_details.price_per_unit

    def get_cost_per_unit(self, plan: UUID) -> Decimal:
        request = GetPlanDetailsInteractor.Request(plan)
        response = self.get_plan_details.get_plan_details(request)
        assert response
        return response.plan_details.cost_per_unit
