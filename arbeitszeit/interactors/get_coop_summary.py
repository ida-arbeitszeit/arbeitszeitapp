from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.records import Plan
from arbeitszeit.repositories import DatabaseGateway
from arbeitszeit.services.price_calculator import PriceCalculator


@dataclass
class GetCoopSummaryRequest:
    requester_id: UUID
    coop_id: UUID


@dataclass
class AssociatedPlan:
    plan_id: UUID
    plan_name: str
    plan_individual_price: Decimal
    planner_id: UUID
    planner_name: str
    requester_is_planner: bool


@dataclass
class GetCoopSummaryResponse:
    requester_is_coordinator: bool
    coop_id: UUID
    coop_name: str
    coop_definition: str
    current_coordinator: UUID
    current_coordinator_name: str
    coop_price: Optional[Decimal]
    plans: List[AssociatedPlan]


@dataclass
class GetCoopSummaryInteractor:
    database_gateway: DatabaseGateway
    price_calculator: PriceCalculator
    datetime_service: DatetimeService

    def execute(
        self, request: GetCoopSummaryRequest
    ) -> Optional[GetCoopSummaryResponse]:
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
        plan_result = (
            self.database_gateway.get_plans()
            .that_are_part_of_cooperation(request.coop_id)
            .that_will_expire_after(now)
        )
        plans = list(plan_result)
        return GetCoopSummaryResponse(
            requester_is_coordinator=coordinator.id == request.requester_id,
            coop_id=coop.id,
            coop_name=coop.name,
            coop_definition=coop.definition,
            current_coordinator=coordinator.id,
            current_coordinator_name=coordinator.name,
            coop_price=self._get_cooperative_price(plans),
            plans=self._get_associated_plans(plans, request.requester_id),
        )

    def _get_planner_name(self, planner_id: UUID) -> str:
        planner = self.database_gateway.get_companies().with_id(planner_id).first()
        assert planner
        return planner.name

    def _get_cooperative_price(self, plans: list[Plan]) -> Optional[Decimal]:
        if not plans:
            return None
        return self.price_calculator.calculate_cooperative_price(plans[0].id)

    def _get_associated_plans(
        self, plans: list[Plan], requester: UUID
    ) -> list[AssociatedPlan]:
        return [
            AssociatedPlan(
                plan_id=plan.id,
                plan_name=plan.prd_name,
                plan_individual_price=plan.price_per_unit(),
                planner_id=plan.planner,
                planner_name=self._get_planner_name(plan.planner),
                requester_is_planner=plan.planner == requester,
            )
            for plan in plans
        ]
