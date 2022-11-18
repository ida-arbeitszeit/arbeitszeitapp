from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol
from uuid import UUID

from injector import inject

from arbeitszeit import errors
from arbeitszeit.entities import Member, Plan
from arbeitszeit.repositories import MemberRepository, PlanRepository

from .consumer_product_transaction import (
    ConsumerProductTransaction,
    ConsumerProductTransactionFactory,
)
from .rejection_reason import RejectionReason


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


@inject
@dataclass
class PayConsumerProduct:
    member_repository: MemberRepository
    plan_repository: PlanRepository
    transaction_factory: ConsumerProductTransactionFactory

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
        buyer = self.member_repository.get_by_id(request.get_buyer_id())
        if buyer is None:
            return PayConsumerProductResponse(
                rejection_reason=RejectionReason.buyer_does_not_exist
            )
        transaction = self._create_product_transaction(plan, request, buyer)
        if not transaction.is_account_balance_sufficient():
            return PayConsumerProductResponse(
                rejection_reason=RejectionReason.insufficient_balance
            )
        transaction.record_purchase()
        transaction.exchange_currency()
        return PayConsumerProductResponse(rejection_reason=None)

    def _get_active_plan(self, request: PayConsumerProductRequest) -> Plan:
        plan = self.plan_repository.get_plan_by_id(request.get_plan_id())
        if plan is None:
            raise self.PlanNotFound("Plan could not be found")
        if not plan.is_active:
            raise errors.PlanIsInactive(
                plan=plan,
            )
        return plan

    def _create_product_transaction(
        self, plan: Plan, request: PayConsumerProductRequest, buyer: Member
    ) -> ConsumerProductTransaction:
        return self.transaction_factory.create_consumer_product_transaction(
            buyer=buyer,
            plan=plan,
            amount=request.get_amount(),
        )

    class PlanNotFound(ValueError):
        pass
