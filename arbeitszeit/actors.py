from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Optional, Protocol
from uuid import UUID

from arbeitszeit.entities import Member as MemberEntity
from arbeitszeit.entities import Plan


class Member(Protocol):
    def pay_for_product(self, plan: Plan, amount: int) -> TransactionReceipt:
        ...

    def get_planning_information(self, plan_id: UUID) -> Optional[Plan]:
        ...


class GiroOffice(Protocol):
    def conduct_consumer_transaction(
        self, transaction: ConsumerProductTransaction
    ) -> TransactionReceipt:
        ...


class MemberRepository(Protocol):
    def get_by_id(self, member_id: UUID) -> Optional[Member]:
        ...


@dataclass(frozen=True)
class TransactionReceipt:
    rejection_reason: Optional[TransactionRejection]

    @property
    def is_success(self) -> bool:
        return self.rejection_reason is None


@enum.unique
class TransactionRejection(enum.Enum):
    insufficient_balance = enum.auto()


@dataclass
class ConsumerProductTransaction:
    buyer: MemberEntity
    plan: Plan
    amount: int
