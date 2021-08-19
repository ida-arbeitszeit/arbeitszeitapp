from dataclasses import dataclass
from typing import Optional

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Plan
from arbeitszeit.repositories import PlanRepository


@inject
@dataclass
class SeekApproval:
    datetime_service: DatetimeService
    plan_repository: PlanRepository

    def __call__(self, new_plan: Plan, original_plan: Optional[Plan]) -> bool:
        """
        Company seeks plan approval. Either for a new plan or for a plan reneweal.
        Sets approved either to True or False, sets approval_date and approval_reason.

        Additionally, if it's a plan renewal, the original plan will be set to "renewed".
        Returns the approval decision.
        """
        # This is just a place holder
        is_approval = True
        approval_date = self.datetime_service.now()
        if is_approval:
            new_plan.approve(approval_date)
            if original_plan:
                self.plan_repository.renew_plan(original_plan)
        else:
            new_plan.deny(approval_date)
        return is_approval
