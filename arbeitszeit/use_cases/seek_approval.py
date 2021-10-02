from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import PlanDraft
from arbeitszeit.repositories import PlanDraftRepository, PlanRepository


@dataclass
class SeekApprovalResponse:
    is_approved: bool
    reason: str


@inject
@dataclass
class SeekApproval:
    datetime_service: DatetimeService
    plan_repository: PlanRepository
    draft_repository: PlanDraftRepository

    def __call__(
        self, new_plan_id: UUID, original_plan_id: Optional[UUID]
    ) -> SeekApprovalResponse:
        plan = self.draft_repository.get_by_id(new_plan_id)
        assert plan is not None
        if original_plan_id:
            reason = self.renew_plan(plan, original_plan_id)
        else:
            reason = self.approve_plan(plan)
        return SeekApprovalResponse(
            is_approved=True,
            reason=reason,
        )

    def renew_plan(self, draft: PlanDraft, original_plan_id: UUID) -> str:
        original_plan = self.plan_repository.get_plan_by_id(original_plan_id)
        assert original_plan is not None
        self.plan_repository.renew_plan(original_plan)
        return self.approve_plan(draft)

    def approve_plan(self, draft: PlanDraft) -> str:
        new_plan = self.plan_repository.approve_plan(draft, self.get_approval_date())
        self.draft_repository.delete_draft(draft.id)
        assert new_plan.approval_reason
        return new_plan.approval_reason

    def get_approval_date(self) -> datetime:
        return self.datetime_service.now()
