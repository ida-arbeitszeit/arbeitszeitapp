from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.repositories import PlanDraftRepository, PlanRepository


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

    def file_plan_with_accounting(self, request: Request) -> Response:
        draft = self.draft_repository.get_by_id(id=request.draft_id)
        if draft is not None and draft.planner.id == request.filing_company:
            self.draft_repository.delete_draft(id=request.draft_id)
            plan_id = self.plan_repository.create_plan(
                plan=self.plan_repository.CreatePlan(
                    planner=draft.planner.id,
                    product_name=draft.product_name,
                    description=draft.description,
                    costs=draft.production_costs,
                    production_unit=draft.unit_of_distribution,
                    amount=draft.amount_produced,
                    timeframe_in_days=draft.timeframe,
                    is_public_service=draft.is_public_service,
                    creation_timestamp=self.datetime_service.now(),
                )
            )
            is_plan_successfully_filed = True
        else:
            plan_id = None
            is_plan_successfully_filed = False
        return self.Response(
            is_plan_successfully_filed=is_plan_successfully_filed,
            plan_id=plan_id,
        )