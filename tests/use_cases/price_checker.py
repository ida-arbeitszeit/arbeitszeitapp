from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from injector import inject

from arbeitszeit.use_cases.get_plan_summary_member import GetPlanSummaryMember


@inject
@dataclass
class PriceChecker:
    get_plan_summary_member: GetPlanSummaryMember

    def get_unit_price(self, plan: UUID) -> Decimal:
        response = self.get_plan_summary_member(plan)
        assert isinstance(response, GetPlanSummaryMember.Success)
        return response.plan_summary.price_per_unit

    def get_unit_cost(self, plan: UUID) -> Decimal:
        response = self.get_plan_summary_member(plan)
        assert isinstance(response, GetPlanSummaryMember.Success)
        summary = response.plan_summary
        return (
            summary.means_cost + summary.resources_cost + summary.labour_cost
        ) / summary.amount
