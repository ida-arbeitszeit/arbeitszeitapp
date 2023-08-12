from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Tuple
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.price_calculator import PriceCalculator
from arbeitszeit.records import Company, Plan, PurposesOfPurchases
from arbeitszeit.repositories import DatabaseGateway


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


@dataclass(frozen=True)
class PayMeansOfProduction:
    price_calculator: PriceCalculator
    datetime_service: DatetimeService
    database_gateway: DatabaseGateway

    def __call__(
        self, request: PayMeansOfProductionRequest
    ) -> PayMeansOfProductionResponse:
        try:
            plan, buyer, purpose = self._validate_request(request)
        except PayMeansOfProductionResponse.RejectionReason as reason:
            return PayMeansOfProductionResponse(rejection_reason=reason)
        self.create_transaction(
            buyer=buyer, plan=plan, amount=request.amount, purpose=purpose
        )
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
        now = self.datetime_service.now()
        plan = self.database_gateway.get_plans().with_id(request.plan).first()
        if plan is None:
            raise PayMeansOfProductionResponse.RejectionReason.plan_not_found
        if not plan.is_active_as_of(now):
            raise PayMeansOfProductionResponse.RejectionReason.plan_is_not_active
        if plan.is_public_service:
            raise PayMeansOfProductionResponse.RejectionReason.cannot_buy_public_service
        return plan

    def _validate_buyer_is_not_planner(
        self, request: PayMeansOfProductionRequest, plan: Plan
    ) -> Company:
        if plan.planner == request.buyer:
            raise PayMeansOfProductionResponse.RejectionReason.buyer_is_planner
        buyer = self.database_gateway.get_companies().with_id(request.buyer).first()
        assert buyer is not None
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

    def create_transaction(
        self, amount: int, purpose: PurposesOfPurchases, buyer: Company, plan: Plan
    ) -> None:
        coop_price = amount * self.price_calculator.calculate_cooperative_price(plan)
        individual_price = amount * self.price_calculator.calculate_individual_price(
            plan
        )
        if purpose == PurposesOfPurchases.means_of_prod:
            sending_account = buyer.means_account
        elif purpose == PurposesOfPurchases.raw_materials:
            sending_account = buyer.raw_material_account
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
        self.database_gateway.create_company_purchase(
            amount=amount,
            transaction=transaction.id,
            plan=plan.id,
        )
