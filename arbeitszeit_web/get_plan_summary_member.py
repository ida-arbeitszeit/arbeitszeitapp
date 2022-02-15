from dataclasses import asdict, dataclass
from typing import Any, Dict

from arbeitszeit.use_cases.get_plan_summary_member import PlanSummarySuccess
from arbeitszeit_web.plan_summary_service import PlanSummary, PlanSummaryService

from .translator import Translator


@dataclass
class GetPlanSummaryViewModel:
    summary: PlanSummary

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GetPlanSummarySuccessPresenter:
    trans: Translator
    plan_summary_service: PlanSummaryService

    def present(self, response: PlanSummarySuccess) -> GetPlanSummaryViewModel:
        return GetPlanSummaryViewModel(
            summary=self.plan_summary_service.get_plan_summary_member(
                response.plan_summary
            )
        )
