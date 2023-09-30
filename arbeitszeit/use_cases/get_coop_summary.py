from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
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
    planner_id: UUID
    planner_name: str


@dataclass
class GetCoopSummarySuccess:
    requester_is_coordinator: bool
    coop_id: UUID
    coop_name: str
    coop_definition: str
    current_coordinator: UUID
    current_coordinator_name: str

    plans: List[AssociatedPlan]


GetCoopSummaryResponse = Optional[GetCoopSummarySuccess]


@dataclass
class GetCoopSummary:
    database_gateway: DatabaseGateway
    price_calculator: PriceCalculator
    datetime_service: DatetimeService

    def __call__(self, request: GetCoopSummaryRequest) -> GetCoopSummaryResponse:
        coop_and_coordinator = (
            self.database_gateway.get_cooperations()
            .with_id(request.coop_id)
            .joined_with_current_coordinator()
            .first()
        )
        if coop_and_coordinator is None:
            return None
        coop, coordinator = coop_and_coordinator
        now = self.datetime_service.now()
        plans = [
            AssociatedPlan(
                plan_id=plan.id,
                plan_name=plan.prd_name,
                plan_individual_price=plan.production_costs.total_cost()
                / plan.prd_amount
                if not plan.is_public_service
                else Decimal(0),
                plan_coop_price=self.price_calculator.calculate_cooperative_price(plan),
                planner_id=plan.planner,
                planner_name=self._get_planner_name(plan.planner),
            )
            for plan in self.database_gateway.get_plans()
            .that_are_part_of_cooperation(request.coop_id)
            .that_will_expire_after(now)
        ]
        return GetCoopSummarySuccess(
            requester_is_coordinator=coordinator.id == request.requester_id,
            coop_id=coop.id,
            coop_name=coop.name,
            coop_definition=coop.definition,
            current_coordinator=coordinator.id,
            current_coordinator_name=coordinator.name,
            plans=plans,
        )

    def _get_planner_name(self, planner_id: UUID) -> str:
        planner = self.database_gateway.get_companies().with_id(planner_id).first()
        assert planner
        return planner.name
