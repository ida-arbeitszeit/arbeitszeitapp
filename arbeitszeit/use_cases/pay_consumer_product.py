from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Protocol
from uuid import UUID

from injector import inject

from arbeitszeit.actors import MemberRepository


class RejectionReason(Exception, Enum):
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

    def __call__(
        self, request: PayConsumerProductRequest
    ) -> PayConsumerProductResponse:
        try:
            return self._conduct_payment(request)
        except RejectionReason as reason:
            return PayConsumerProductResponse(rejection_reason=reason)

    def _conduct_payment(
        self, request: PayConsumerProductRequest
    ) -> PayConsumerProductResponse:
        member = self.member_repository.get_by_id(request.get_buyer_id())
        assert member
        plan = member.get_planning_information(request.get_plan_id())
        if plan is None:
            raise RejectionReason.plan_not_found
        if not plan.is_active:
            raise RejectionReason.plan_inactive
        receipt = member.pay_for_product(plan=plan, amount=request.get_amount())
        if not receipt.is_success:
            raise RejectionReason.insufficient_balance
        return PayConsumerProductResponse(rejection_reason=None)
