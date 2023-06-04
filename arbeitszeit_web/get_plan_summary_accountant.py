from dataclasses import asdict, dataclass
from typing import Any, Dict

from arbeitszeit.use_cases.get_plan_summary import GetPlanSummaryUseCase
from arbeitszeit_web.formatters.plan_summary_formatter import (
    PlanSummaryFormatter,
    PlanSummaryWeb,
)
from arbeitszeit_web.url_index import UrlIndex

from .translator import Translator


@dataclass
class GetPlanSummaryAccountantViewModel:
    summary: PlanSummaryWeb

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GetPlanSummaryAccountantPresenter:
    trans: Translator
    plan_summary_service: PlanSummaryFormatter
    url_index: UrlIndex

    def present(
        self, response: GetPlanSummaryUseCase.Response
    ) -> GetPlanSummaryAccountantViewModel:
        return GetPlanSummaryAccountantViewModel(
            summary=self.plan_summary_service.format_plan_summary(
                response.plan_summary
            ),
        )
