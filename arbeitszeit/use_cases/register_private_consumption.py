from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from arbeitszeit.control_thresholds import ControlThresholds
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.price_calculator import PriceCalculator
from arbeitszeit.records import Company, Member, Plan, Transfer
from arbeitszeit.repositories import DatabaseGateway
from arbeitszeit.transfers.compensation import CompensationTransferService
from arbeitszeit.transfers.transfer_type import TransferType


class RejectionReason(Exception, Enum):
    plan_inactive = auto()
    plan_not_found = auto()
    insufficient_balance = auto()
    consumer_does_not_exist = auto()


@dataclass
class RegisterPrivateConsumptionRequest:
    consumer: UUID
    plan: UUID
    amount: int


@dataclass
class RegisterPrivateConsumptionResponse:
    rejection_reason: Optional[RejectionReason]

    @property
    def is_accepted(self) -> bool:
        return self.rejection_reason is None


@dataclass
class RegisterPrivateConsumption:
    control_thresholds: ControlThresholds
    datetime_service: DatetimeService
    price_calculator: PriceCalculator
    database_gateway: DatabaseGateway
    compensation_transfer_service: CompensationTransferService

    def register_private_consumption(
        self, request: RegisterPrivateConsumptionRequest
    ) -> RegisterPrivateConsumptionResponse:
        try:
            return self._perform_registration_process(request)
        except RejectionReason as reason:
            return RegisterPrivateConsumptionResponse(rejection_reason=reason)

    def _perform_registration_process(
        self, request: RegisterPrivateConsumptionRequest
    ) -> RegisterPrivateConsumptionResponse:
        plan, planner = self._get_plan_and_planner(request)
        consumer = self._get_consumer(request)
        coop_price_per_unit = self.price_calculator.calculate_cooperative_price(plan)
        consumption_transfer = self._create_private_consumption_transfer(
            debit_account=consumer.account,
            credit_account=planner.product_account,
            value=coop_price_per_unit * request.amount,
        )
        compensation_transfer = self._get_compensation_transfer_if_any(
            plan_id=plan.id,
            planner_product_account=planner.product_account,
            plan_price_per_unit=plan.price_per_unit(),
            coop_price_per_unit=coop_price_per_unit,
            consumed_amount=request.amount,
        )
        self.database_gateway.create_private_consumption(
            amount=request.amount,
            plan=plan.id,
            transfer_of_private_consumption=consumption_transfer.id,
            transfer_of_compensation=compensation_transfer,
        )
        return RegisterPrivateConsumptionResponse(rejection_reason=None)

    def _get_plan_and_planner(
        self, request: RegisterPrivateConsumptionRequest
    ) -> tuple[Plan, Company]:
        plan = self._get_active_plan(request)
        planner = self.database_gateway.get_companies().with_id(plan.planner).first()
        assert planner  # Each plan has a planner.
        return plan, planner

    def _get_consumer(self, request: RegisterPrivateConsumptionRequest) -> Member:
        consumer = self.database_gateway.get_members().with_id(request.consumer).first()
        if consumer is None:
            raise RejectionReason.consumer_does_not_exist
        return consumer

    def _create_private_consumption_transfer(
        self,
        debit_account: UUID,
        credit_account: UUID,
        value: Decimal,
    ) -> Transfer:
        if not self._is_account_balance_sufficient(value, debit_account):
            raise RejectionReason.insufficient_balance
        transfer = self.database_gateway.create_transfer(
            date=self.datetime_service.now(),
            debit_account=debit_account,
            credit_account=credit_account,
            value=value,
            type=TransferType.private_consumption,
        )
        return transfer

    def _is_account_balance_sufficient(
        self, transfer_value: Decimal, account: UUID
    ) -> bool:
        if transfer_value <= 0:
            return True
        allowed_overdraw = (
            self.control_thresholds.get_allowed_overdraw_of_member_account()
        )
        if allowed_overdraw is None:
            return True
        account_balance = self._get_account_balance(account)
        if account_balance is None:
            return False
        if transfer_value > account_balance + allowed_overdraw:
            return False
        return True

    def _get_account_balance(self, account: UUID) -> Optional[Decimal]:
        result = (
            self.database_gateway.get_accounts()
            .with_id(account)
            .joined_with_balance()
            .first()
        )
        if result:
            return result[1]
        else:
            return None

    def _get_active_plan(self, request: RegisterPrivateConsumptionRequest) -> Plan:
        now = self.datetime_service.now()
        plan = self.database_gateway.get_plans().with_id(request.plan).first()
        if plan is None:
            raise RejectionReason.plan_not_found
        if not plan.is_active_as_of(now):
            raise RejectionReason.plan_inactive
        return plan

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
