from dataclasses import dataclass
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

    def __call__(self, new_plan_id: UUID) -> SeekApprovalResponse:
        """
        Company seeks plan approval.
        Sets approved either to True or False, sets approval_date and approval_reason.

        Returns the approval decision.
        """
        new_plan = self.plan_repository.get_plan_by_id(new_plan_id)
        is_approval = True
        approval_date = self.datetime_service.now()
        if is_approval:
            new_plan.approve(approval_date)
        else:
            new_plan.deny(approval_date)
        assert new_plan.approval_reason
        return SeekApprovalResponse(
            is_approved=is_approval,
            reason=new_plan.approval_reason,
        )
