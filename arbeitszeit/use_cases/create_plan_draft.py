from dataclasses import dataclass
from uuid import UUID

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import ProductionCosts
from arbeitszeit.repositories import PlanDraftRepository


@dataclass
class CreatePlanDraftRequest:
    costs: ProductionCosts
    product_name: str
    production_unit: str
    production_amount: int
    description: str
    timeframe_in_days: int
    is_public_service: bool
    planner: UUID


@dataclass
class CreatePlanDraftResponse:
    draft_id: UUID


@inject
@dataclass
class CreatePlanDraft:
    plan_draft_repository: PlanDraftRepository
    datetime_service: DatetimeService

    def __call__(self, request: CreatePlanDraftRequest) -> CreatePlanDraftResponse:
        draft = self.plan_draft_repository.create_plan_draft(
            planner=request.planner,
            costs=request.costs,
            product_name=request.product_name,
            production_unit=request.production_unit,
            amount=request.production_amount,
            description=request.description,
            timeframe_in_days=request.timeframe_in_days,
            is_public_service=request.is_public_service,
            creation_timestamp=self.datetime_service.now(),
        )
        return CreatePlanDraftResponse(draft_id=draft.id)
