from decimal import Decimal

from arbeitszeit.plan_summary import BusinessPlanSummary
from arbeitszeit_web.plan_summary_service import PlanSummary


class FakePlanSummaryService:
    def get_plan_summary_member(self, plan_summary: BusinessPlanSummary) -> PlanSummary:
        ...

    def __format_price(self, price_per_unit: Decimal) -> str:
        ...
