from dataclasses import asdict, dataclass
from decimal import Decimal
from typing import Any, Dict, List

from arbeitszeit.use_cases.get_coop_summary import GetCoopSummarySuccess
from arbeitszeit_web.session import Session

from ...url_index import UrlIndex, UserUrlIndex


@dataclass
class AssociatedPlanPresentation:
    plan_name: str
    plan_url: str
    plan_individual_price: str
    plan_coop_price: str
    end_coop_url: str


@dataclass
class GetCoopSummaryViewModel:
    show_end_coop_button: bool
    coop_id: str
    coop_name: str
    coop_definition: List[str]
    current_coordinator_id: str
    current_coordinator_name: str
    current_coordinator_url: str

    plans: List[AssociatedPlanPresentation]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GetCoopSummarySuccessPresenter:
    user_url_index: UserUrlIndex
    url_index: UrlIndex
    session: Session

    def present(self, response: GetCoopSummarySuccess) -> GetCoopSummaryViewModel:
        return GetCoopSummaryViewModel(
            show_end_coop_button=response.requester_is_coordinator,
            coop_id=str(response.coop_id),
            coop_name=response.coop_name,
            coop_definition=response.coop_definition.splitlines(),
            current_coordinator_id=str(response.current_coordinator),
            current_coordinator_name=response.current_coordinator_name,
            current_coordinator_url=self.url_index.get_company_summary_url(
                user_role=self.session.get_user_role(),
                company_id=response.current_coordinator,
            ),
            plans=[
                AssociatedPlanPresentation(
                    plan_name=plan.plan_name,
                    plan_url=self.user_url_index.get_plan_details_url(plan.plan_id),
                    plan_individual_price=self.__format_price(
                        plan.plan_individual_price
                    ),
                    plan_coop_price=self.__format_price(plan.plan_coop_price),
                    end_coop_url=self.url_index.get_end_coop_url(
                        plan_id=plan.plan_id, cooperation_id=response.coop_id
                    ),
                )
                for plan in response.plans
            ],
        )

    def __format_price(self, price_per_unit: Decimal) -> str:
        return f"{round(price_per_unit, 2)}"
