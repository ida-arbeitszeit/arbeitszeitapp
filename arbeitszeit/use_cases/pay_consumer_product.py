from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Protocol
from uuid import UUID

from injector import inject

from arbeitszeit.actors import MemberRepository
from arbeitszeit.repositories import PlanRepository


class RejectionReason(Enum):
    plan_inactive = auto()
    plan_not_found = auto()
    insufficient_balance = auto()


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

    def __call__(
        self, request: PayConsumerProductRequest
    ) -> PayConsumerProductResponse:
        rejection_reason: Optional[RejectionReason]
        plan = self.plan_repository.get_plan_by_id(request.get_plan_id())
        if plan is None:
            return PayConsumerProductResponse(
                rejection_reason=RejectionReason.plan_not_found
            )
        if not plan.is_active:
            return PayConsumerProductResponse(
                rejection_reason=RejectionReason.plan_inactive
            )
        member = self.member_repository.get_by_id(request.get_buyer_id())
        assert member
        receipt = member.pay_for_product(plan=plan, amount=request.get_amount())
        if receipt.is_success:
            rejection_reason = None
        else:
            rejection_reason = RejectionReason.insufficient_balance
        return PayConsumerProductResponse(rejection_reason=rejection_reason)
