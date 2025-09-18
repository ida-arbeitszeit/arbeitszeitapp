from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class Request:
    plan: UUID
    company: UUID


@dataclass
class Response:
    draft: Optional[UUID]

    def is_rejected(self) -> bool:
        return not self.draft


@dataclass
class CreateDraftFromPlanInteractor:
    database: DatabaseGateway
    datetime_service: DatetimeService

    def create_draft_from_plan(self, request: Request) -> Response:
        if not self.database.get_companies().with_id(request.company):
            return Response(draft=None)
        plan = self.database.get_plans().with_id(request.plan).first()
        if not plan:
            return Response(draft=None)
        draft = self.database.create_plan_draft(
            planner=request.company,
            product_name=plan.prd_name,
            description=plan.description,
            costs=plan.production_costs,
            production_unit=plan.prd_unit,
            amount=plan.prd_amount,
            timeframe_in_days=plan.timeframe,
            is_public_service=plan.is_public_service,
            creation_timestamp=self.datetime_service.now(),
        )
        return Response(draft=draft.id)
