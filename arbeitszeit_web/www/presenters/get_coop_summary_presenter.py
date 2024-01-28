from dataclasses import asdict, dataclass
from decimal import Decimal
from typing import Any, Dict, List, Optional

from arbeitszeit.use_cases.get_coop_summary import GetCoopSummaryResponse

from ...url_index import UrlIndex, UserUrlIndex


@dataclass
class AssociatedPlan:
    plan_name: str
    plan_url: str
    plan_individual_price: str
    end_coop_url: str
    planner_name: str
    planner_url: str
    show_end_coop_button: bool


@dataclass
class GetCoopSummaryViewModel:
    coop_id: str
    coop_name: str
    coop_definition: List[str]
    transfer_coordination_url: Optional[str]
    current_coordinator_id: str
    current_coordinator_name: str
    current_coordinator_url: str
    list_of_coordinators_url: str
    coop_price: str

    plans: List[AssociatedPlan]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GetCoopSummarySuccessPresenter:
    user_url_index: UserUrlIndex
    url_index: UrlIndex

    def present(self, response: GetCoopSummaryResponse) -> GetCoopSummaryViewModel:
        return GetCoopSummaryViewModel(
            coop_id=str(response.coop_id),
            coop_name=response.coop_name,
            coop_definition=response.coop_definition.splitlines(),
            transfer_coordination_url=self.url_index.get_request_coordination_transfer_url(
                coop_id=response.coop_id
            )
            if response.requester_is_coordinator
            else None,
            current_coordinator_id=str(response.current_coordinator),
            current_coordinator_name=response.current_coordinator_name,
            current_coordinator_url=self.url_index.get_company_summary_url(
                company_id=response.current_coordinator,
            ),
            list_of_coordinators_url=self.url_index.get_list_of_coordinators_url(
                cooperation_id=response.coop_id,
            ),
            coop_price="-"
            if response.coop_price is None
            else self.__format_price(response.coop_price),
            plans=[
                AssociatedPlan(
                    plan_name=plan.plan_name,
                    plan_url=self.user_url_index.get_plan_details_url(plan.plan_id),
                    plan_individual_price=self.__format_price(
                        plan.plan_individual_price
                    ),
                    end_coop_url=self.url_index.get_end_coop_url(
                        plan_id=plan.plan_id, cooperation_id=response.coop_id
                    ),
                    planner_name=plan.planner_name,
                    planner_url=self.url_index.get_company_summary_url(
                        company_id=plan.planner_id
                    ),
                    show_end_coop_button=response.requester_is_coordinator
                    or plan.requester_is_planner,
                )
                for plan in response.plans
            ],
        )

    def __format_price(self, price_per_unit: Decimal) -> str:
        return f"{round(price_per_unit, 2)}"
