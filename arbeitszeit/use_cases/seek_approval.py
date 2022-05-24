from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Plan, PlanDraft
from arbeitszeit.repositories import PlanDraftRepository, PlanRepository


@inject
@dataclass
class SeekApproval:
    @dataclass
    class Request:
        draft_id: UUID

    @dataclass
    class Response:
        is_approved: bool
        reason: str
        new_plan_id: UUID

    datetime_service: DatetimeService
    plan_repository: PlanRepository
    draft_repository: PlanDraftRepository

    def __call__(self, request: Request) -> Response:
        draft = self.draft_repository.get_by_id(request.draft_id)
        assert draft is not None
        new_plan = self.approve_plan_and_delete_draft(draft)
        assert new_plan.approval_reason
        return self.Response(
            is_approved=True, reason=new_plan.approval_reason, new_plan_id=new_plan.id
        )

    def approve_plan_and_delete_draft(self, draft: PlanDraft) -> Plan:
        new_plan = self.plan_repository.set_plan_approval_date(
            draft, self.get_approval_date()
        )
        self.draft_repository.delete_draft(draft.id)
        return new_plan

    def get_approval_date(self) -> datetime:
        return self.datetime_service.now()
