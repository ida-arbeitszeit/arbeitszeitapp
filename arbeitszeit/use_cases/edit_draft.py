from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from uuid import UUID

from arbeitszeit.repositories import PlanDraftRepository


@dataclass
class EditDraftUseCase:
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
        is_success: bool

    draft_repository: PlanDraftRepository

    def edit_draft(self, request: Request) -> Response:
        if (
            (draft := self.draft_repository.get_by_id(request.draft)) is not None
        ) and draft.planner.id == request.editor:
            self.draft_repository.update_draft(
                update=self.draft_repository.UpdateDraft(
                    id=request.draft,
                    product_name=request.product_name,
                    amount=request.amount,
                    description=request.description,
                    labour_cost=request.labour_cost,
                    means_cost=request.means_cost,
                    resource_cost=request.resource_cost,
                    is_public_service=request.is_public_service,
                    timeframe=request.timeframe,
                    unit_of_distribution=request.unit_of_distribution,
                )
            )
            is_success = True
        else:
            is_success = False
        return self.Response(
            is_success=is_success,
        )
