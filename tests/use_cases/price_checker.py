from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from arbeitszeit.use_cases.get_plan_details import GetPlanDetailsUseCase


@dataclass
class PriceChecker:
    get_plan_details: GetPlanDetailsUseCase

    def get_unit_price(self, plan: UUID) -> Decimal:
        request = GetPlanDetailsUseCase.Request(plan)
        response = self.get_plan_details.get_plan_details(request)
        assert response
        return response.plan_details.price_per_unit

    def get_labour_per_unit(self, plan: UUID) -> Decimal:
        request = GetPlanDetailsUseCase.Request(plan)
        response = self.get_plan_details.get_plan_details(request)
        assert response
        return response.plan_details.labour_cost_per_unit

    def get_unit_cost(self, plan: UUID) -> Decimal:
        request = GetPlanDetailsUseCase.Request(plan)
        response = self.get_plan_details.get_plan_details(request)
        assert response
        details = response.plan_details
        return (
            details.means_cost + details.resources_cost + details.labour_cost
        ) / details.amount
