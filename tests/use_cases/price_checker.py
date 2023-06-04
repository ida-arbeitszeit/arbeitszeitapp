from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from arbeitszeit.use_cases.get_plan_summary import GetPlanSummaryUseCase


@dataclass
class PriceChecker:
    get_plan_summary: GetPlanSummaryUseCase

    def get_unit_price(self, plan: UUID) -> Decimal:
        response = self.get_plan_summary.get_plan_summary(plan)
        assert isinstance(response, GetPlanSummaryUseCase.Success)
        return response.plan_summary.price_per_unit

    def get_unit_cost(self, plan: UUID) -> Decimal:
        response = self.get_plan_summary.get_plan_summary(plan)
        assert isinstance(response, GetPlanSummaryUseCase.Success)
        summary = response.plan_summary
        return (
            summary.means_cost + summary.resources_cost + summary.labour_cost
        ) / summary.amount
