from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional

from arbeitszeit.use_cases.get_plan_summary_company import PlanSummaryCompanySuccess

from .plan_summary_service import PlanSummary, PlanSummaryService
from .translator import Translator
from .url_index import (
    EndCoopUrlIndex,
    RequestCoopUrlIndex,
    TogglePlanAvailabilityUrlIndex,
)


@dataclass
class Action:
    is_available: bool
    toggle_availability_url: str
    is_cooperating: bool
    end_coop_url: Optional[str]
    request_coop_url: Optional[str]


@dataclass
class GetPlanSummaryCompanyViewModel:
    summary: PlanSummary
    show_action_section: bool
    action: Action

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GetPlanSummaryCompanySuccessPresenter:
    toggle_availability_url_index: TogglePlanAvailabilityUrlIndex
    end_coop_url_index: EndCoopUrlIndex
    request_coop_url_index: RequestCoopUrlIndex
    trans: Translator
    plan_summary_service: PlanSummaryService

    def present(
        self, response: PlanSummaryCompanySuccess
    ) -> GetPlanSummaryCompanyViewModel:
        plan_id = response.plan_summary.plan_id
        coop_id = response.plan_summary.cooperation
        is_available = response.plan_summary.is_available
        is_cooperating = response.plan_summary.is_cooperating
        return GetPlanSummaryCompanyViewModel(
            summary=self.plan_summary_service.get_plan_summary(response.plan_summary),
            show_action_section=response.current_user_is_planner,
            action=Action(
                is_available=is_available,
                toggle_availability_url=self.toggle_availability_url_index.get_toggle_availability_url(
                    plan_id
                ),
                is_cooperating=is_cooperating,
                end_coop_url=self.end_coop_url_index.get_end_coop_url(plan_id, coop_id)
                if coop_id
                else None,
                request_coop_url=self.request_coop_url_index.get_request_coop_url()
                if not is_cooperating
                else None,
            ),
        )
