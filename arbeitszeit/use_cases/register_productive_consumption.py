from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Tuple
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.price_calculator import PriceCalculator
from arbeitszeit.records import Company, ConsumptionType, Plan
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class RegisterProductiveConsumptionRequest:
    consumer: UUID
    plan: UUID
    amount: int
    consumption_type: ConsumptionType


@dataclass
class RegisterProductiveConsumptionResponse:
    class RejectionReason(Exception, Enum):
        plan_not_found = auto()
        invalid_consumption_type = auto()
        cannot_consume_public_service = auto()
        plan_is_not_active = auto()
        consumer_is_planner = auto()
        plan_is_rejected = auto()

    rejection_reason: Optional[RejectionReason]

    @property
    def is_rejected(self) -> bool:
        return self.rejection_reason is not None


@dataclass(frozen=True)
class RegisterProductiveConsumption:
    price_calculator: PriceCalculator
    datetime_service: DatetimeService
    database_gateway: DatabaseGateway

    def __call__(
        self, request: RegisterProductiveConsumptionRequest
    ) -> RegisterProductiveConsumptionResponse:
        try:
            plan, consumer, purpose = self._validate_request(request)
        except RegisterProductiveConsumptionResponse.RejectionReason as reason:
            return RegisterProductiveConsumptionResponse(rejection_reason=reason)
        self._create_transaction(
            consumer=consumer,
            plan=plan,
            amount=request.amount,
            consumption_type=purpose,
        )
        return RegisterProductiveConsumptionResponse(rejection_reason=None)

    def _validate_request(
        self, request: RegisterProductiveConsumptionRequest
    ) -> Tuple[Plan, Company, ConsumptionType]:
        plan = self._validate_plan(request)
        return (
            plan,
            self._validate_consumer_is_not_planner(request, plan),
            self._validate_purpose(request),
        )

    def _validate_plan(self, request: RegisterProductiveConsumptionRequest) -> Plan:
        now = self.datetime_service.now()
        plan = self.database_gateway.get_plans().with_id(request.plan).first()
        if plan is None:
            raise RegisterProductiveConsumptionResponse.RejectionReason.plan_not_found
        if plan.is_rejected:
            raise RegisterProductiveConsumptionResponse.RejectionReason.plan_is_rejected
        if not plan.is_active_as_of(now):
            raise RegisterProductiveConsumptionResponse.RejectionReason.plan_is_not_active
        if plan.is_public_service:
            raise RegisterProductiveConsumptionResponse.RejectionReason.cannot_consume_public_service
        return plan

    def _validate_consumer_is_not_planner(
        self, request: RegisterProductiveConsumptionRequest, plan: Plan
    ) -> Company:
        if plan.planner == request.consumer:
            raise RegisterProductiveConsumptionResponse.RejectionReason.consumer_is_planner
        consumer = (
            self.database_gateway.get_companies().with_id(request.consumer).first()
        )
        assert consumer is not None
        return consumer

    def _validate_purpose(
        self, request: RegisterProductiveConsumptionRequest
    ) -> ConsumptionType:
        if request.consumption_type not in (
            ConsumptionType.means_of_prod,
            ConsumptionType.raw_materials,
        ):
            raise RegisterProductiveConsumptionResponse.RejectionReason.invalid_consumption_type
        return request.consumption_type

    def _create_transaction(
        self,
        amount: int,
        consumption_type: ConsumptionType,
        consumer: Company,
        plan: Plan,
    ) -> None:
        coop_price = amount * self.price_calculator.calculate_cooperative_price(plan)
        individual_price = amount * plan.price_per_unit()
        if consumption_type == ConsumptionType.means_of_prod:
            sending_account = consumer.means_account
        elif consumption_type == ConsumptionType.raw_materials:
            sending_account = consumer.raw_material_account
        planner = self.database_gateway.get_companies().with_id(plan.planner).first()
        assert planner
        transaction = self.database_gateway.create_transaction(
            date=self.datetime_service.now(),
            sending_account=sending_account,
            receiving_account=planner.product_account,
            amount_sent=coop_price,
            amount_received=individual_price,
            purpose=f"Plan-Id: {plan.id}",
        )
        self.database_gateway.create_productive_consumption(
            amount=amount,
            transaction=transaction.id,
            plan=plan.id,
        )
