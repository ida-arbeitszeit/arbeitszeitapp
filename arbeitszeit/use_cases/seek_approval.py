from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.repositories import PlanRepository


@dataclass
class SeekApprovalResponse:
    is_approved: bool
    reason: str


@inject
@dataclass
class SeekApproval:
    datetime_service: DatetimeService
    plan_repository: PlanRepository

    def __call__(
        self, new_plan_id: UUID, original_plan_id: Optional[UUID]
    ) -> SeekApprovalResponse:
        """
        Company seeks plan approval. Either for a new plan or for a plan reneweal.
        Sets approved either to True or False, sets approval_date and approval_reason.

        Additionally, if it's a plan renewal, the original plan will be set to "renewed".
        Returns the approval decision.
        """
        new_plan = self.plan_repository.get_plan_by_id(new_plan_id)
        original_plan = (
            None
            if original_plan_id is None
            else self.plan_repository.get_plan_by_id(original_plan_id)
        )
        approval_date = self.datetime_service.now()
        self.plan_repository.approve_plan(new_plan, approval_date)
        if original_plan:
            self.plan_repository.renew_plan(original_plan)
        assert new_plan.approval_reason
        return SeekApprovalResponse(
            is_approved=True,
            reason=new_plan.approval_reason,
        )
