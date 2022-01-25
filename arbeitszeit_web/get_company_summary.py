from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List

from arbeitszeit.use_cases.get_company_summary import (
    GetCompanySummarySuccess,
    PlanDetails,
)


@dataclass
class PlanDetailsWeb:
    id: str
    name: str


@dataclass
class GetCompanySummaryViewModel:
    name: str
    email: str
    registered_on: datetime
    active_plans: List[PlanDetailsWeb]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GetCompanySummarySuccessPresenter:
    def present(
        self, use_case_response: GetCompanySummarySuccess
    ) -> GetCompanySummaryViewModel:
        return GetCompanySummaryViewModel(
            use_case_response.name,
            use_case_response.email,
            use_case_response.registered_on,
            [self._get_plan_details(plan) for plan in use_case_response.active_plans],
        )

    def _get_plan_details(self, plan_details: PlanDetails) -> PlanDetailsWeb:
        return PlanDetailsWeb(str(plan_details.id), plan_details.name)
