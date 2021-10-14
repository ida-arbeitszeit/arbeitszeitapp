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
        self, draft_id: UUID, expired_plan_id: Optional[UUID]
    ) -> SeekApprovalResponse:
        draft = self.draft_repository.get_by_id(draft_id)
        assert draft is not None
        if expired_plan_id:
            self.set_expired_plan_as_renewed(expired_plan_id)
        reason = self.approve_plan_and_delete_draft(draft)
        return SeekApprovalResponse(
            is_approved=True,
            reason=reason,
        )

    def set_expired_plan_as_renewed(self, expired_plan_id: UUID) -> None:
        expired_plan = self.plan_repository.get_plan_by_id(expired_plan_id)
        assert expired_plan is not None
        self.plan_repository.set_plan_as_renewed(expired_plan)

    def approve_plan_and_delete_draft(self, draft: PlanDraft) -> str:
        new_plan = self.plan_repository.approve_plan(draft, self.get_approval_date())
        self.draft_repository.delete_draft(draft.id)
        assert new_plan.approval_reason
        return new_plan.approval_reason

    def get_approval_date(self) -> datetime:
        return self.datetime_service.now()
