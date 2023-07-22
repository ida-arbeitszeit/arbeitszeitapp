from dataclasses import asdict, dataclass
from typing import Any, Dict

from arbeitszeit.use_cases.get_plan_details import GetPlanDetailsUseCase
from arbeitszeit_web.formatters.plan_details_formatter import (
    PlanDetailsFormatter,
    PlanDetailsWeb,
)
from arbeitszeit_web.url_index import UrlIndex

from ...translator import Translator


@dataclass
class GetPlanDetailsAccountantViewModel:
    details: PlanDetailsWeb

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GetPlanDetailsAccountantPresenter:
    trans: Translator
    plan_details_service: PlanDetailsFormatter
    url_index: UrlIndex

    def present(
        self, response: GetPlanDetailsUseCase.Response
    ) -> GetPlanDetailsAccountantViewModel:
        return GetPlanDetailsAccountantViewModel(
            details=self.plan_details_service.format_plan_details(
                response.plan_details
            ),
        )
