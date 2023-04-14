from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from arbeitszeit.price_calculator import PriceCalculator
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class GetCoopSummaryRequest:
    requester_id: UUID
    coop_id: UUID


@dataclass
class AssociatedPlan:
    plan_id: UUID
    plan_name: str
    plan_individual_price: Decimal
    plan_coop_price: Decimal


@dataclass
class GetCoopSummarySuccess:
    requester_is_coordinator: bool
    coop_id: UUID
    coop_name: str
    coop_definition: str
    coordinator_id: UUID
    coordinator_name: str

    plans: List[AssociatedPlan]


GetCoopSummaryResponse = Optional[GetCoopSummarySuccess]


@dataclass
class GetCoopSummary:
    database_gateway: DatabaseGateway
    price_calculator: PriceCalculator

    def __call__(self, request: GetCoopSummaryRequest) -> GetCoopSummaryResponse:
        coop_and_coordinator = (
            self.database_gateway.get_cooperations()
            .with_id(request.coop_id)
            .joined_with_coordinator()
            .first()
        )
        if coop_and_coordinator is None:
            return None
        coop, coordinator = coop_and_coordinator
        plans = [
            AssociatedPlan(
                plan_id=plan.id,
                plan_name=plan.prd_name,
                plan_individual_price=plan.production_costs.total_cost()
                / plan.prd_amount
                if not plan.is_public_service
                else Decimal(0),
                plan_coop_price=self.price_calculator.calculate_cooperative_price(plan),
            )
            for plan in self.database_gateway.get_plans().that_are_part_of_cooperation(
                request.coop_id
            )
        ]
        return GetCoopSummarySuccess(
            requester_is_coordinator=coop.coordinator == request.requester_id,
            coop_id=coop.id,
            coop_name=coop.name,
            coop_definition=coop.definition,
            coordinator_id=coop.coordinator,
            coordinator_name=coordinator.name,
            plans=plans,
        )
