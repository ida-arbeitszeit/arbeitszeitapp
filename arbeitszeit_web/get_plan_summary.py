from arbeitszeit.use_cases.get_plan_summary import PlanSummaryResponse
from dataclasses import dataclass


@dataclass
class GetPlanSummaryViewModel:
    product_name: str
    description: str
    timeframe: str
    production_unit: str
    amount: str
    means_cost: str
    resources_cost: str
    labour_cost: str
    type_of_plan: str


class GetPlanSummaryPresenter:
    def present(self, response: PlanSummaryResponse) -> GetPlanSummaryViewModel:
        return GetPlanSummaryViewModel(
            product_name=response.product_name,
            description=response.description,
            timeframe=str(response.timeframe),
            production_unit=response.production_unit,
            amount=str(response.amount),
            means_cost=str(response.means_cost),
            resources_cost=str(response.resources_cost),
            labour_cost=str(response.labour_cost),
            type_of_plan="Öffentlich" if response.is_public_service else "Produktiv",
        )
