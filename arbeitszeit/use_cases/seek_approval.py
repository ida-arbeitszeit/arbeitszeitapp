from dataclasses import dataclass
from typing import Optional

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Plan
from arbeitszeit.use_cases import GrantCredit


@inject
@dataclass
class SeekApproval:
    grant_credit: GrantCredit
    datetime_service: DatetimeService

    def __call__(self, new_plan: Plan, original_plan: Optional[Plan]) -> bool:
        """
        Company seeks plan approval. Either for a new plan or for a plan reneweal.
        If approved, credit is granted.
        Additionally, if it's a plan renewal, the original plan will be set to "renewed".
        Returns a boolian value.
        """
        # This is just a place holder
        is_approval = True
        approval_date = self.datetime_service.now()
        if is_approval:
            new_plan.approve(approval_date)
            self.grant_credit(new_plan)
            if original_plan:
                original_plan.set_as_renewed()
        else:
            new_plan.deny(approval_date)
        return is_approval
