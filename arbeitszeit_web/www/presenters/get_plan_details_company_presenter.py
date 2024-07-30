from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional

from arbeitszeit.plan_details import PlanDetails
from arbeitszeit.use_cases.get_plan_details import GetPlanDetailsUseCase
from arbeitszeit_web.formatters.plan_details_formatter import (
    PlanDetailsFormatter,
    PlanDetailsWeb,
)
from arbeitszeit_web.session import Session

from ...url_index import UrlIndex


@dataclass
class OwnPlanAction:
    is_cooperating: bool
    end_coop_url: Optional[str]
    request_coop_url: Optional[str]


@dataclass
class GetPlanDetailsCompanyViewModel:
    details: PlanDetailsWeb
    show_own_plan_action_section: bool
    own_plan_action: OwnPlanAction
    show_productive_consumption_url: bool
    productive_consumption_url: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GetPlanDetailsCompanyPresenter:
    plan_details_service: PlanDetailsFormatter
    url_index: UrlIndex
    session: Session

    def present(
        self, response: GetPlanDetailsUseCase.Response
    ) -> GetPlanDetailsCompanyViewModel:
        plan_details = response.plan_details
        current_user = self.session.get_current_user()
        assert current_user
        current_user_is_planner = response.plan_details.planner_id == current_user
        show_own_plan_action_section = (
            current_user_is_planner and plan_details.is_active
        )
        view_model = GetPlanDetailsCompanyViewModel(
            details=self.plan_details_service.format_plan_details(plan_details),
            show_own_plan_action_section=show_own_plan_action_section,
            own_plan_action=self._create_own_plan_action_section(plan_details),
            show_productive_consumption_url=(
                True if not current_user_is_planner else False
            ),
            productive_consumption_url=self.url_index.get_select_productive_consumption_url(
                plan_details.plan_id
            ),
        )
        return view_model

    def _create_own_plan_action_section(self, plan: PlanDetails) -> OwnPlanAction:
        section = OwnPlanAction(
            is_cooperating=plan.is_cooperating,
            end_coop_url=(
                self.url_index.get_end_coop_url(
                    plan_id=plan.plan_id, cooperation_id=plan.cooperation
                )
                if (plan.cooperation and plan.is_cooperating)
                else None
            ),
            request_coop_url=(
                self.url_index.get_request_coop_url()
                if not plan.is_cooperating
                else None
            ),
        )
        return section
