from dataclasses import asdict, dataclass
from decimal import Decimal
from typing import Any, Dict, List

from arbeitszeit.use_cases.get_coop_summary import GetCoopSummarySuccess


@dataclass
class AssociatedPlanPresentation:
    plan_id: str
    plan_name: str
    plan_total_costs: str
    plan_amount: str
    plan_individual_price: str
    plan_coop_price: str


@dataclass
class GetCoopSummaryViewModel:
    show_end_coop_button: bool
    coop_id: str
    coop_name: str
    coop_definition: List[str]
    coordinator_id: str

    plans: List[AssociatedPlanPresentation]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class GetCoopSummarySuccessPresenter:
    def present(self, response: GetCoopSummarySuccess) -> GetCoopSummaryViewModel:
        return GetCoopSummaryViewModel(
            show_end_coop_button=response.requester_is_coordinator,
            coop_id=str(response.coop_id),
            coop_name=response.coop_name,
            coop_definition=response.coop_definition.splitlines(),
            coordinator_id=str(response.coordinator_id),
            plans=[
                AssociatedPlanPresentation(
                    plan_id=str(plan.plan_id),
                    plan_name=plan.plan_name,
                    plan_total_costs=str(plan.plan_total_costs),
                    plan_amount=str(plan.plan_amount),
                    plan_individual_price=self.__format_price(
                        plan.plan_individual_price
                    ),
                    plan_coop_price=self.__format_price(plan.plan_coop_price),
                )
                for plan in response.plans
            ],
        )

    def __format_price(self, price_per_unit: Decimal) -> str:
        return f"{round(price_per_unit, 2)}"
