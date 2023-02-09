from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum, auto
from typing import Optional, Protocol
from uuid import UUID

from arbeitszeit import errors
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Member, Plan
from arbeitszeit.giro_office import GiroOffice, TransactionRejection
from arbeitszeit.price_calculator import PriceCalculator
from arbeitszeit.repositories import (
    CompanyRepository,
    MemberRepository,
    PlanRepository,
    PurchaseRepository,
)


class RejectionReason(Enum):
    plan_inactive = auto()
    plan_not_found = auto()
    insufficient_balance = auto()
    buyer_does_not_exist = auto()


class PayConsumerProductRequest(Protocol):
    def get_buyer_id(self) -> UUID:
        ...

    def get_plan_id(self) -> UUID:
        ...

    def get_amount(self) -> int:
        ...


@dataclass
class PayConsumerProductResponse:
    rejection_reason: Optional[RejectionReason]

    @property
    def is_accepted(self) -> bool:
        return self.rejection_reason is None


@dataclass
class PayConsumerProduct:
    member_repository: MemberRepository
    plan_repository: PlanRepository
    giro_office: GiroOffice
    datetime_service: DatetimeService
    purchase_repository: PurchaseRepository
    company_repository: CompanyRepository
    price_calculator: PriceCalculator

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
        buyer = (
            self.member_repository.get_members().with_id(request.get_buyer_id()).first()
        )
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
                request.get_amount(),
                plan,
                buyer,
                coop_price_per_unit=coop_price_per_unit,
                individual_price_per_unit=individual_price_per_unit,
            )
        except TransactionRejection:
            return PayConsumerProductResponse(
                rejection_reason=RejectionReason.insufficient_balance
            )
        self._record_purchase(
            plan_id=plan.id,
            amount=request.get_amount(),
            buyer_id=buyer.id,
            price_per_unit=coop_price_per_unit,
        )
        return PayConsumerProductResponse(rejection_reason=None)

    def _get_active_plan(self, request: PayConsumerProductRequest) -> Plan:
        plan = self.plan_repository.get_plans().with_id(request.get_plan_id()).first()
        if plan is None:
            raise self.PlanNotFound("Plan could not be found")
        if not plan.is_active:
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
        self.giro_office.record_transaction_from_member(
            sender=buyer,
            receiving_account=planner.product_account,
            amount_sent=coop_price_per_unit * amount,
            amount_received=individual_price_per_unit * amount,
            purpose=f"Plan-Id: {plan.id}",
        )

    def _record_purchase(
        self, plan_id: UUID, amount: int, buyer_id: UUID, price_per_unit: Decimal
    ) -> None:
        self.purchase_repository.create_purchase_by_member(
            purchase_date=self.datetime_service.now(),
            plan=plan_id,
            buyer=buyer_id,
            price_per_unit=price_per_unit,
            amount=amount,
        )
