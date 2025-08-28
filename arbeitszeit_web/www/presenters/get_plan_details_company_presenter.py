from dataclasses import dataclass
from typing import Optional

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
    plan_id: str
    cooperation_id: str | None
    request_coop_url: Optional[str]


@dataclass
class GetPlanDetailsCompanyViewModel:
    details: PlanDetailsWeb
    show_own_plan_action_section: bool
    own_plan_action: OwnPlanAction
    show_productive_consumption_url: bool
    productive_consumption_url: str


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
            productive_consumption_url=self.url_index.get_register_productive_consumption_url(
                plan_details.plan_id
            ),
        )
        return view_model

    def _create_own_plan_action_section(self, plan: PlanDetails) -> OwnPlanAction:
        section = OwnPlanAction(
            is_cooperating=plan.is_cooperating,
            plan_id=str(plan.plan_id),
            cooperation_id=str(plan.cooperation) if plan.cooperation else None,
            request_coop_url=(
                self.url_index.get_request_coop_url()
                if not plan.is_cooperating
                else None
            ),
        )
        return section
