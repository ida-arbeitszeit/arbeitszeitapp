from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional

from injector import inject

from arbeitszeit.use_cases.get_plan_summary_company import GetPlanSummaryCompany
from arbeitszeit_web.formatters.plan_summary_formatter import (
    PlanSummaryFormatter,
    PlanSummaryWeb,
)

from .translator import Translator
from .url_index import UrlIndex


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


@inject
@dataclass
class GetPlanSummaryCompanySuccessPresenter:
    trans: Translator
    plan_summary_service: PlanSummaryFormatter
    url_index: UrlIndex

    def present(
        self, response: GetPlanSummaryCompany.Response
    ) -> GetPlanSummaryCompanyViewModel:
        plan_summary = response.plan_summary
        assert plan_summary is not None
        plan_id = plan_summary.plan_id
        coop_id = plan_summary.cooperation
        is_cooperating = plan_summary.is_cooperating
        show_own_plan_action_section = (
            response.current_user_is_planner and plan_summary.is_active
        )
        return GetPlanSummaryCompanyViewModel(
            summary=self.plan_summary_service.format_plan_summary(plan_summary),
            show_own_plan_action_section=show_own_plan_action_section,
            own_plan_action=OwnPlanAction(
                is_available_bool=plan_summary.is_available,
                toggle_availability_url=self.url_index.get_toggle_availability_url(
                    plan_id
                ),
                is_cooperating=is_cooperating,
                end_coop_url=self.url_index.get_end_coop_url(
                    plan_id=plan_id, cooperation_id=coop_id
                )
                if coop_id
                else None,
                request_coop_url=self.url_index.get_request_coop_url()
                if not is_cooperating
                else None,
            ),
            show_payment_url=True if not response.current_user_is_planner else False,
            payment_url=self.url_index.get_pay_means_of_production_url(plan_id),
        )
