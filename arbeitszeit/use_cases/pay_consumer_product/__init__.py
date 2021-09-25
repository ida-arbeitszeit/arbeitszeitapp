from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from injector import inject

from arbeitszeit import errors
from arbeitszeit.entities import Plan
from arbeitszeit.repositories import MemberRepository, PlanRepository

from .consumer_product_transaction import (
    ConsumerProductTransaction,
    ConsumerProductTransactionFactory,
)


class PayConsumerProductRequest(Protocol):
    def get_buyer_id(self) -> UUID:
        ...

    def get_plan_id(self) -> UUID:
        ...

    def get_amount(self) -> int:
        ...


class PayConsumerProductResponse:
    pass


@inject
@dataclass
class PayConsumerProduct:
    member_repository: MemberRepository
    plan_repository: PlanRepository
    transaction_factory: ConsumerProductTransactionFactory

    def __call__(
        self, request: PayConsumerProductRequest
    ) -> PayConsumerProductResponse:
        plan = self.plan_repository.get_plan_by_id(request.get_plan_id())
        self._ensure_plan_is_active(plan)
        transaction = self._create_product_transaction(plan, request)
        transaction.record_purchase()
        transaction.exchange_currency()
        return PayConsumerProductResponse()

    def _ensure_plan_is_active(self, plan: Plan) -> None:
        if not plan.is_active:
            raise errors.PlanIsInactive(
                plan=plan,
            )

    def _create_product_transaction(
        self, plan: Plan, request: PayConsumerProductRequest
    ) -> ConsumerProductTransaction:
        return self.transaction_factory.create_consumer_product_transaction(
            buyer=self.member_repository.get_by_id(request.get_buyer_id()),
            plan=plan,
            amount=request.get_amount(),
        )
