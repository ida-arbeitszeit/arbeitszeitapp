from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Tuple
from uuid import UUID

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Company, Member, Plan, PurposesOfPurchases
from arbeitszeit.price_calculator import calculate_price
from arbeitszeit.repositories import (
    CompanyRepository,
    PlanCooperationRepository,
    PlanRepository,
    PurchaseRepository,
    TransactionRepository,
)


@dataclass
class PayMeansOfProductionRequest:
    buyer: UUID
    plan: UUID
    amount: int
    purpose: PurposesOfPurchases


@dataclass
class PayMeansOfProductionResponse:
    class RejectionReason(Exception, Enum):
        plan_not_found = auto()
        invalid_purpose = auto()
        cannot_buy_public_service = auto()
        plan_is_not_active = auto()
        buyer_is_planner = auto()

    rejection_reason: Optional[RejectionReason]

    @property
    def is_rejected(self) -> bool:
        return self.rejection_reason is not None


@inject
@dataclass(frozen=True)
class PayMeansOfProduction:
    plan_repository: PlanRepository
    company_repository: CompanyRepository
    payment_factory: PaymentFactory

    def __call__(
        self, request: PayMeansOfProductionRequest
    ) -> PayMeansOfProductionResponse:
        try:
            plan, buyer, purpose = self._validate_request(request)
        except PayMeansOfProductionResponse.RejectionReason as reason:
            return PayMeansOfProductionResponse(rejection_reason=reason)
        payment = self.payment_factory.get_payment(plan, buyer, request.amount, purpose)
        payment.record_purchase()
        payment.create_transaction()
        return PayMeansOfProductionResponse(rejection_reason=None)

    def _validate_request(
        self, request: PayMeansOfProductionRequest
    ) -> Tuple[Plan, Company, PurposesOfPurchases]:
        plan = self._validate_plan(request)
        return (
            plan,
            self._validate_buyer_is_not_planner(request, plan),
            self._validate_purpose(request),
        )

    def _validate_plan(self, request: PayMeansOfProductionRequest) -> Plan:
        plan = self.plan_repository.get_plan_by_id(request.plan)
        if plan is None:
            raise PayMeansOfProductionResponse.RejectionReason.plan_not_found
        if not plan.is_active:
            raise PayMeansOfProductionResponse.RejectionReason.plan_is_not_active
        if plan.is_public_service:
            raise PayMeansOfProductionResponse.RejectionReason.cannot_buy_public_service
        return plan

    def _validate_buyer_is_not_planner(
        self, request: PayMeansOfProductionRequest, plan: Plan
    ) -> Company:
        buyer = self.company_repository.get_by_id(request.buyer)
        assert buyer is not None
        if plan.planner == buyer:
            raise PayMeansOfProductionResponse.RejectionReason.buyer_is_planner
        return buyer

    def _validate_purpose(
        self, request: PayMeansOfProductionRequest
    ) -> PurposesOfPurchases:
        if request.purpose not in (
            PurposesOfPurchases.means_of_prod,
            PurposesOfPurchases.raw_materials,
        ):
            raise PayMeansOfProductionResponse.RejectionReason.invalid_purpose
        return request.purpose


@dataclass
class Payment:
    purchase_repository: PurchaseRepository
    transaction_repository: TransactionRepository
    datetime_service: DatetimeService
    plan_cooperation_repository: PlanCooperationRepository
    plan: Plan
    buyer: Company
    amount: int
    purpose: PurposesOfPurchases

    def record_purchase(self) -> None:
        price_per_unit = calculate_price(
            self.plan_cooperation_repository.get_cooperating_plans(self.plan.id)
        )
        self.purchase_repository.create_purchase(
            purchase_date=self.datetime_service.now(),
            plan=self.plan.id,
            buyer=self.buyer.id,
            is_buyer_a_member=isinstance(self.buyer, Member),
            price_per_unit=price_per_unit,
            amount=self.amount,
            purpose=self.purpose,
        )

    def create_transaction(self) -> None:
        coop_price = self.amount * calculate_price(
            self.plan_cooperation_repository.get_cooperating_plans(self.plan.id)
        )
        individual_price = self.amount * calculate_price([self.plan])
        if self.purpose == PurposesOfPurchases.means_of_prod:
            sending_account = self.buyer.means_account
        elif self.purpose == PurposesOfPurchases.raw_materials:
            sending_account = self.buyer.raw_material_account

        self.transaction_repository.create_transaction(
            date=self.datetime_service.now(),
            sending_account=sending_account,
            receiving_account=self.plan.planner.product_account,
            amount_sent=coop_price,
            amount_received=individual_price,
            purpose=f"Plan-Id: {self.plan.id}",
        )


@inject
@dataclass
class PaymentFactory:
    purchase_repository: PurchaseRepository
    transaction_repository: TransactionRepository
    datetime_service: DatetimeService
    plan_cooperation_repository: PlanCooperationRepository

    def get_payment(
        self, plan: Plan, buyer: Company, amount: int, purpose: PurposesOfPurchases
    ) -> Payment:
        return Payment(
            self.purchase_repository,
            self.transaction_repository,
            self.datetime_service,
            self.plan_cooperation_repository,
            plan,
            buyer,
            amount,
            purpose,
        )
