from arbeitszeit.use_cases import ListPlansResponse
from typing import List
from dataclasses import dataclass


@dataclass
class ListedPlan:
    id: str
    prd_name: str


@dataclass
class ListPlansViewModel:
    plans: List[ListedPlan]


class ListPlansPresenter:
    def present(self, use_case_response: ListPlansResponse) -> ListPlansViewModel:
        plans = [
            ListedPlan(id=str(plan.id), prd_name=plan.prd_name)
            for plan in use_case_response.plans
        ]
        return ListPlansViewModel(plans=plans)
