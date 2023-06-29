from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import ProductionCosts
from arbeitszeit.repositories import DatabaseGateway


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
    class RejectionReason(Exception, Enum):
        negative_plan_input = auto()
        planner_does_not_exist = auto()

    draft_id: Optional[UUID]
    rejection_reason: Optional[RejectionReason]

    @property
    def is_rejected(self) -> bool:
        return self.rejection_reason is not None


@dataclass
class CreatePlanDraft:
    database: DatabaseGateway
    datetime_service: DatetimeService

    def __call__(self, request: CreatePlanDraftRequest) -> CreatePlanDraftResponse:
        if (
            request.costs.labour_cost < 0
            or request.costs.means_cost < 0
            or request.costs.resource_cost < 0
            or request.production_amount < 0
            or request.timeframe_in_days < 0
        ):
            return CreatePlanDraftResponse(
                draft_id=None,
                rejection_reason=CreatePlanDraftResponse.RejectionReason.negative_plan_input,
            )
        if not self.database.get_companies().with_id(request.planner):
            return CreatePlanDraftResponse(
                draft_id=None,
                rejection_reason=CreatePlanDraftResponse.RejectionReason.planner_does_not_exist,
            )

        draft = self.database.create_plan_draft(
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
        return CreatePlanDraftResponse(draft_id=draft.id, rejection_reason=None)
