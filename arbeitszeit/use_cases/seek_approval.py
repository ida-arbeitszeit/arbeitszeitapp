from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Plan, PlanDraft
from arbeitszeit.repositories import PlanDraftRepository, PlanRepository


@dataclass
class SeekApprovalResponse:
    is_approved: bool
    reason: str
    new_plan_id: UUID


@inject
@dataclass
class SeekApproval:
    datetime_service: DatetimeService
    plan_repository: PlanRepository
    draft_repository: PlanDraftRepository

    def __call__(self, draft_id: UUID) -> SeekApprovalResponse:
        draft = self.draft_repository.get_by_id(draft_id)
        assert draft is not None
        new_plan = self.approve_plan_and_delete_draft(draft)
        assert new_plan.approval_reason
        return SeekApprovalResponse(
            is_approved=True, reason=new_plan.approval_reason, new_plan_id=new_plan.id
        )

    def approve_plan_and_delete_draft(self, draft: PlanDraft) -> Plan:
        new_plan = self.plan_repository.approve_plan(draft, self.get_approval_date())
        self.draft_repository.delete_draft(draft.id)
        return new_plan

    def get_approval_date(self) -> datetime:
        return self.datetime_service.now()
