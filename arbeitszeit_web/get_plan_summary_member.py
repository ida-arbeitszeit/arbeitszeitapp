from dataclasses import asdict, dataclass
from typing import Any, Dict

from arbeitszeit.use_cases.get_plan_summary_member import GetPlanSummaryMember
from arbeitszeit_web.plan_summary_service import PlanSummaryFormatter, PlanSummaryWeb

from .translator import Translator


@dataclass
class GetPlanSummaryViewModel:
    summary: PlanSummaryWeb

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GetPlanSummarySuccessPresenter:
    trans: Translator
    plan_summary_service: PlanSummaryFormatter

    def present(
        self, response: GetPlanSummaryMember.Success
    ) -> GetPlanSummaryViewModel:
        return GetPlanSummaryViewModel(
            summary=self.plan_summary_service.format_plan_summary(response.plan_summary)
        )
