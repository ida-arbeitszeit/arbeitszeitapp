from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from arbeitszeit import errors
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Member, Plan
from arbeitszeit.giro_office import GiroOffice, TransactionRejection
from arbeitszeit.price_calculator import PriceCalculator
from arbeitszeit.repositories import (
    CompanyRepository,
    DatabaseGateway,
    MemberRepository,
)


class RejectionReason(Enum):
    plan_inactive = auto()
    plan_not_found = auto()
    insufficient_balance = auto()
    buyer_does_not_exist = auto()


@dataclass
class PayConsumerProductRequest:
    buyer: UUID
    plan: UUID
    amount: int


@dataclass
class PayConsumerProductResponse:
    rejection_reason: Optional[RejectionReason]

    @property
    def is_accepted(self) -> bool:
        return self.rejection_reason is None


@dataclass
class PayConsumerProduct:
    member_repository: MemberRepository
    giro_office: GiroOffice
    datetime_service: DatetimeService
    company_repository: CompanyRepository
    price_calculator: PriceCalculator
    database_gateway: DatabaseGateway

    def pay_consumer_product(
        self, request: PayConsumerProductRequest
    ) -> PayConsumerProductResponse:
        try:
            return self._perform_buying_process(request)
        except errors.PlanIsInactive:
            return PayConsumerProductResponse(
                rejection_reason=RejectionReason.plan_inactive
            )
        except self.PlanNotFound:
            return PayConsumerProductResponse(
                rejection_reason=RejectionReason.plan_not_found
            )

    def _perform_buying_process(
        self, request: PayConsumerProductRequest
    ) -> PayConsumerProductResponse:
        plan = self._get_active_plan(request)
        buyer = self.member_repository.get_members().with_id(request.buyer).first()
        if buyer is None:
            return PayConsumerProductResponse(
                rejection_reason=RejectionReason.buyer_does_not_exist
            )
        coop_price_per_unit = self.price_calculator.calculate_cooperative_price(plan)
        individual_price_per_unit = self.price_calculator.calculate_individual_price(
            plan
        )
        try:
            self._transfer_certificates(
                request.amount,
                plan,
                buyer,
                coop_price_per_unit=coop_price_per_unit,
                individual_price_per_unit=individual_price_per_unit,
            )
        except TransactionRejection:
            return PayConsumerProductResponse(
                rejection_reason=RejectionReason.insufficient_balance
            )
        return PayConsumerProductResponse(rejection_reason=None)

    def _get_active_plan(self, request: PayConsumerProductRequest) -> Plan:
        now = self.datetime_service.now()
        plan = self.database_gateway.get_plans().with_id(request.plan).first()
        if plan is None:
            raise self.PlanNotFound("Plan could not be found")
        if not plan.is_active_as_of(now):
            raise errors.PlanIsInactive(
                plan=plan,
            )
        return plan

    class PlanNotFound(ValueError):
        pass

    def _transfer_certificates(
        self,
        amount: int,
        plan: Plan,
        buyer: Member,
        coop_price_per_unit: Decimal,
        individual_price_per_unit: Decimal,
    ) -> None:
        planner = self.company_repository.get_companies().with_id(plan.planner).first()
        assert planner
        transaction = self.giro_office.record_transaction_from_member(
            sender=buyer,
            receiving_account=planner.product_account,
            amount_sent=coop_price_per_unit * amount,
            amount_received=individual_price_per_unit * amount,
            purpose=f"Plan-Id: {plan.id}",
        )
        self.database_gateway.create_consumer_purchase(
            amount=amount,
            plan=plan.id,
            transaction=transaction.id,
        )
