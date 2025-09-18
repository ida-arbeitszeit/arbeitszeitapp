import enum
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from uuid import UUID

from arbeitszeit.repositories import DatabaseGateway


@dataclass
class Request:
    draft: UUID
    editor: UUID
    product_name: Optional[str]
    amount: Optional[int]
    description: Optional[str]
    labour_cost: Optional[Decimal]
    means_cost: Optional[Decimal]
    resource_cost: Optional[Decimal]
    is_public_service: Optional[bool]
    timeframe: Optional[int]
    unit_of_distribution: Optional[str]


@dataclass
class Response:
    @dataclass
    class RejectionReason(enum.Enum):
        NOT_FOUND = enum.auto()
        UNAUTHORIZED = enum.auto()

    rejection_reason: RejectionReason | None


@dataclass
class EditDraftInteractor:
    database: DatabaseGateway

    def edit_draft(self, request: Request) -> Response:
        draft = self.database.get_plan_drafts().with_id(request.draft).first()
        if draft is None:
            return Response(rejection_reason=Response.RejectionReason.NOT_FOUND)
        elif draft.planner != request.editor:
            return Response(rejection_reason=Response.RejectionReason.UNAUTHORIZED)
        else:
            update = self.database.get_plan_drafts().with_id(request.draft).update()
            if request.product_name is not None:
                update = update.set_product_name(request.product_name)
            if request.amount is not None:
                update = update.set_amount(request.amount)
            if request.description is not None:
                update = update.set_description(request.description)
            if request.labour_cost is not None:
                update = update.set_labour_cost(request.labour_cost)
            if request.means_cost is not None:
                update = update.set_means_cost(request.means_cost)
            if request.resource_cost is not None:
                update = update.set_resource_cost(request.resource_cost)
            if request.is_public_service is not None:
                update = update.set_is_public_service(request.is_public_service)
            if request.timeframe is not None:
                update = update.set_timeframe(request.timeframe)
            if request.unit_of_distribution is not None:
                update = update.set_unit_of_distribution(request.unit_of_distribution)
            update.perform()
            return Response(rejection_reason=None)
