from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum, auto
from typing import Optional, Tuple
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.records import Company, ConsumptionType, Plan, Transfer
from arbeitszeit.repositories import DatabaseGateway
from arbeitszeit.services.compensation_transfers import CompensationTransferService
from arbeitszeit.services.price_calculator import PriceCalculator
from arbeitszeit.transfers import TransferType


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
class RegisterProductiveConsumptionInteractor:
    price_calculator: PriceCalculator
    datetime_service: DatetimeService
    database_gateway: DatabaseGateway
    compensation_transfer_service: CompensationTransferService

    def execute(
        self, request: RegisterProductiveConsumptionRequest
    ) -> RegisterProductiveConsumptionResponse:
        try:
            plan, consumer, consumption_type = self._validate_request(request)
        except RegisterProductiveConsumptionResponse.RejectionReason as reason:
            return RegisterProductiveConsumptionResponse(rejection_reason=reason)
        self._perform_registration_process(
            consumer=consumer,
            plan=plan,
            consumed_amount=request.amount,
            consumption_type=consumption_type,
        )
        return RegisterProductiveConsumptionResponse(rejection_reason=None)

    def _validate_request(
        self, request: RegisterProductiveConsumptionRequest
    ) -> Tuple[Plan, Company, ConsumptionType]:
        plan = self._validate_plan(request)
        return (
            plan,
            self._validate_consumer_is_not_planner(request, plan),
            self._validate_consumption_type(request),
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

    def _validate_consumption_type(
        self, request: RegisterProductiveConsumptionRequest
    ) -> ConsumptionType:
        if request.consumption_type not in (
            ConsumptionType.means_of_prod,
            ConsumptionType.raw_materials,
        ):
            raise RegisterProductiveConsumptionResponse.RejectionReason.invalid_consumption_type
        return request.consumption_type

    def _perform_registration_process(
        self,
        consumed_amount: int,
        consumption_type: ConsumptionType,
        consumer: Company,
        plan: Plan,
    ) -> None:
        coop_price_per_unit = self.price_calculator.calculate_cooperative_price(plan)
        planner = self.database_gateway.get_companies().with_id(plan.planner).first()
        assert planner
        consumption_transfer = self._create_productive_consumption_transfer(
            consumption_type=consumption_type,
            consumer=consumer,
            planner_product_account=planner.product_account,
            value=coop_price_per_unit * consumed_amount,
        )
        compensation_transfer = self._get_compensation_transfer_if_any(
            plan_id=plan.id,
            planner_product_account=planner.product_account,
            plan_price_per_unit=plan.price_per_unit(),
            coop_price_per_unit=coop_price_per_unit,
            consumed_amount=consumed_amount,
        )
        self.database_gateway.create_productive_consumption(
            plan=plan.id,
            amount=consumed_amount,
            transfer_of_productive_consumption=consumption_transfer.id,
            transfer_of_compensation=compensation_transfer,
        )

    def _create_productive_consumption_transfer(
        self,
        consumption_type: ConsumptionType,
        consumer: Company,
        planner_product_account: UUID,
        value: Decimal,
    ) -> Transfer:
        if consumption_type == ConsumptionType.means_of_prod:
            debit_account = consumer.means_account
            transfer_type = TransferType.productive_consumption_p
        else:
            debit_account = consumer.raw_material_account
            transfer_type = TransferType.productive_consumption_r
        return self.database_gateway.create_transfer(
            date=self.datetime_service.now(),
            debit_account=debit_account,
            credit_account=planner_product_account,
            value=value,
            type=transfer_type,
        )

    def _get_compensation_transfer_if_any(
        self,
        plan_id: UUID,
        planner_product_account: UUID,
        plan_price_per_unit: Decimal,
        coop_price_per_unit: Decimal,
        consumed_amount: int,
    ) -> UUID | None:
        cooperation = self.database_gateway.get_cooperations().of_plan(plan_id).first()
        if not cooperation:
            return None
        return self.compensation_transfer_service.create_compensation_transfer(
            coop_price_per_unit=coop_price_per_unit,
            plan_price_per_unit=plan_price_per_unit,
            consumed_amount=consumed_amount,
            planner_product_account=planner_product_account,
            cooperation_account=cooperation.account,
        )
