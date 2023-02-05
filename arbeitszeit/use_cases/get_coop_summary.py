from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from arbeitszeit.price_calculator import PriceCalculator
from arbeitszeit.repositories import CooperationRepository, PlanRepository


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
    cooperation_repository: CooperationRepository
    plan_repository: PlanRepository
    price_calculator: PriceCalculator

    def __call__(self, request: GetCoopSummaryRequest) -> GetCoopSummaryResponse:
        coop = self.cooperation_repository.get_by_id(request.coop_id)
        if coop is None:
            return None
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
            for plan in self.plan_repository.get_plans().that_are_part_of_cooperation(
                request.coop_id
            )
        ]
        return GetCoopSummarySuccess(
            requester_is_coordinator=bool(coop.coordinator.id == request.requester_id),
            coop_id=coop.id,
            coop_name=coop.name,
            coop_definition=coop.definition,
            coordinator_id=coop.coordinator.id,
            coordinator_name=coop.coordinator.name,
            plans=plans,
        )
