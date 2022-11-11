from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from injector import inject

from arbeitszeit.accountant_notifications import AccountantNotifier
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.repositories import PlanDraftRepository, PlanRepository


@inject
@dataclass
class FilePlanWithAccounting:
    @dataclass
    class Request:
        draft_id: UUID
        filing_company: UUID

    @dataclass
    class Response:
        is_plan_successfully_filed: bool
        plan_id: Optional[UUID]

    draft_repository: PlanDraftRepository
    plan_repository: PlanRepository
    datetime_service: DatetimeService
    accountant_notifier: AccountantNotifier

    def file_plan_with_accounting(self, request: Request) -> Response:
        draft = self.draft_repository.get_by_id(id=request.draft_id)
        if draft is not None and draft.planner.id == request.filing_company:
            plan_id = self.plan_repository.create_plan_from_draft(
                draft_id=request.draft_id
            )
            assert plan_id
            self.draft_repository.delete_draft(id=request.draft_id)
            is_plan_successfully_filed = True
            self.accountant_notifier.notify_all_accountants_about_new_plan(
                product_name=draft.product_name,
                plan_id=plan_id,
            )
        else:
            plan_id = None
            is_plan_successfully_filed = False
        return self.Response(
            is_plan_successfully_filed=is_plan_successfully_filed,
            plan_id=plan_id,
        )
