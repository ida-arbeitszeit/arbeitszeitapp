from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.giro_office import GiroOffice, Transaction, TransactionRejection
from arbeitszeit.price_calculator import PriceCalculator
from arbeitszeit.records import Member, Plan
from arbeitszeit.repositories import DatabaseGateway


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
    giro_office: GiroOffice
    datetime_service: DatetimeService
    price_calculator: PriceCalculator
    database_gateway: DatabaseGateway

    def register_private_consumption(
        self, request: RegisterPrivateConsumptionRequest
    ) -> RegisterPrivateConsumptionResponse:
        try:
            return self._perform_registration_process(request)
        except RejectionReason as reason:
            return RegisterPrivateConsumptionResponse(rejection_reason=reason)
        except TransactionRejection:
            return RegisterPrivateConsumptionResponse(
                rejection_reason=RejectionReason.insufficient_balance
            )

    def _perform_registration_process(
        self, request: RegisterPrivateConsumptionRequest
    ) -> RegisterPrivateConsumptionResponse:
        plan = self._get_active_plan(request)
        consumer = self.database_gateway.get_members().with_id(request.consumer).first()
        if consumer is None:
            return RegisterPrivateConsumptionResponse(
                rejection_reason=RejectionReason.consumer_does_not_exist
            )
        coop_price_per_unit = self.price_calculator.calculate_cooperative_price(plan)
        transaction = self._transfer_certificates(
            request.amount,
            plan,
            consumer,
            coop_price_per_unit=coop_price_per_unit,
            individual_price_per_unit=plan.price_per_unit(),
        )
        self.database_gateway.create_private_consumption(
            amount=request.amount,
            plan=plan.id,
            transaction=transaction.id,
        )
        return RegisterPrivateConsumptionResponse(rejection_reason=None)

    def _get_active_plan(self, request: RegisterPrivateConsumptionRequest) -> Plan:
        now = self.datetime_service.now()
        plan = self.database_gateway.get_plans().with_id(request.plan).first()
        if plan is None:
            raise RejectionReason.plan_not_found
        if not plan.is_active_as_of(now):
            raise RejectionReason.plan_inactive
        return plan

    def _transfer_certificates(
        self,
        amount: int,
        plan: Plan,
        consumer: Member,
        coop_price_per_unit: Decimal,
        individual_price_per_unit: Decimal,
    ) -> Transaction:
        planner = self.database_gateway.get_companies().with_id(plan.planner).first()
        assert planner
        return self.giro_office.record_transaction_from_member(
            sender=consumer,
            receiving_account=planner.product_account,
            amount_sent=coop_price_per_unit * amount,
            amount_received=individual_price_per_unit * amount,
            purpose=f"Plan-Id: {plan.id}",
        )
