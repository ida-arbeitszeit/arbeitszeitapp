from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional

from arbeitszeit.plan_summary import PlanSummary
from arbeitszeit.use_cases.get_plan_summary import GetPlanSummaryUseCase
from arbeitszeit_web.formatters.plan_summary_formatter import (
    PlanSummaryFormatter,
    PlanSummaryWeb,
)
from arbeitszeit_web.session import Session

from ...url_index import UrlIndex


@dataclass
class OwnPlanAction:
    is_available_bool: bool
    toggle_availability_url: str
    is_cooperating: bool
    end_coop_url: Optional[str]
    request_coop_url: Optional[str]


@dataclass
class GetPlanSummaryCompanyViewModel:
    summary: PlanSummaryWeb
    show_own_plan_action_section: bool
    own_plan_action: OwnPlanAction
    show_payment_url: bool
    payment_url: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GetPlanSummaryCompanyPresenter:
    plan_summary_service: PlanSummaryFormatter
    url_index: UrlIndex
    session: Session

    def present(
        self, response: GetPlanSummaryUseCase.Response
    ) -> GetPlanSummaryCompanyViewModel:
        plan_summary = response.plan_summary
        current_user = self.session.get_current_user()
        assert current_user
        current_user_is_planner = response.plan_summary.planner_id == current_user
        show_own_plan_action_section = (
            current_user_is_planner and plan_summary.is_active
        )
        view_model = GetPlanSummaryCompanyViewModel(
            summary=self.plan_summary_service.format_plan_summary(plan_summary),
            show_own_plan_action_section=show_own_plan_action_section,
            own_plan_action=self._create_own_plan_action_section(plan_summary),
            show_payment_url=True if not current_user_is_planner else False,
            payment_url=self.url_index.get_pay_means_of_production_url(
                plan_summary.plan_id
            ),
        )
        return view_model

    def _create_own_plan_action_section(self, plan: PlanSummary) -> OwnPlanAction:
        section = OwnPlanAction(
            is_available_bool=plan.is_available,
            toggle_availability_url=self.url_index.get_toggle_availability_url(
                plan.plan_id
            ),
            is_cooperating=plan.is_cooperating,
            end_coop_url=self.url_index.get_end_coop_url(
                plan_id=plan.plan_id, cooperation_id=plan.cooperation
            )
            if (plan.cooperation and plan.is_cooperating)
            else None,
            request_coop_url=self.url_index.get_request_coop_url()
            if not plan.is_cooperating
            else None,
        )
        return section
