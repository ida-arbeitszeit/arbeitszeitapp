from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from uuid import UUID

from arbeitszeit.repositories import DatabaseGateway


@dataclass
class DraftSummarySuccess:
    draft_id: UUID
    planner_id: UUID
    product_name: str
    description: str
    timeframe: int
    production_unit: str
    amount: int
    means_cost: Decimal
    resources_cost: Decimal
    labour_cost: Decimal
    is_public_service: bool


DraftSummaryResponse = Optional[DraftSummarySuccess]


@dataclass
class GetDraftSummary:
    database: DatabaseGateway

    def __call__(self, draft_id: UUID) -> DraftSummaryResponse:
        draft = self.database.get_plan_drafts().with_id(draft_id).first()
        if draft is None:
            return None
        return DraftSummarySuccess(
            draft_id=draft.id,
            planner_id=draft.planner,
            product_name=draft.product_name,
            description=draft.description,
            timeframe=draft.timeframe,
            production_unit=draft.unit_of_distribution,
            amount=draft.amount_produced,
            means_cost=draft.production_costs.means_cost,
            resources_cost=draft.production_costs.resource_cost,
            labour_cost=draft.production_costs.labour_cost,
            is_public_service=draft.is_public_service,
        )
