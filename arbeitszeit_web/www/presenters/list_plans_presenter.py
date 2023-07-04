from dataclasses import dataclass
from typing import List

from arbeitszeit.use_cases.list_active_plans_of_company import ListPlansResponse


@dataclass
class ListedPlan:
    id: str
    id_truncated: str
    prd_name_truncated: str


@dataclass
class ListPlansViewModel:
    plans: List[ListedPlan]

    @property
    def show_plan_listing(self) -> bool:
        return bool(self.plans)


class ListPlansPresenter:
    def present(self, use_case_response: ListPlansResponse) -> ListPlansViewModel:
        plans = [
            ListedPlan(
                id=str(plan.id),
                id_truncated=str(plan.id)[:6],
                prd_name_truncated=plan.prd_name[:10],
            )
            for plan in use_case_response.plans
        ]
        return ListPlansViewModel(plans=plans)
