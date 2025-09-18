from dataclasses import dataclass
from typing import List

from arbeitszeit.interactors.list_active_plans_of_company import ListPlansResponse


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
    def present(self, interactor_response: ListPlansResponse) -> ListPlansViewModel:
        plans = [
            ListedPlan(
                id=str(plan.id),
                id_truncated=str(plan.id)[:6],
                prd_name_truncated=plan.prd_name[:10],
            )
            for plan in interactor_response.plans
        ]
        return ListPlansViewModel(plans=plans)
