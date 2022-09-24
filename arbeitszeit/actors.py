from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol
from uuid import UUID

from injector import inject

from arbeitszeit import repositories
from arbeitszeit.entities import Member as MemberEntity
from arbeitszeit.entities import Plan
from arbeitszeit.giro_office import (
    ConsumerProductTransaction,
    GiroOffice,
    TransactionReceipt,
)


class Member(Protocol):
    def pay_for_product(self, plan: Plan, amount: int) -> TransactionReceipt:
        ...


@inject
@dataclass
class MemberRepository:
    member_db_gateway: repositories.MemberRepository
    giro_office: GiroOffice

    def get_by_id(self, member_id: UUID) -> Optional[Member]:
        member = self.member_db_gateway.get_by_id(member_id)
        if member is None:
            return None
        return MemberImpl(
            member=member,
            giro_office=self.giro_office,
        )


@dataclass
class MemberImpl:
    member: MemberEntity
    giro_office: GiroOffice

    def pay_for_product(self, plan: Plan, amount: int) -> TransactionReceipt:
        transaction = ConsumerProductTransaction(
            buyer=self.member,
            plan=plan,
            amount=amount,
        )
        return self.giro_office.conduct_consumer_transaction(transaction)
