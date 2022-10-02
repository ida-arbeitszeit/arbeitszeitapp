from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from injector import inject

from arbeitszeit import repositories
from arbeitszeit.actors import (
    ConsumerProductTransaction,
    GiroOffice,
    Member,
    TransactionReceipt,
)
from arbeitszeit.entities import Member as MemberEntity
from arbeitszeit.entities import Plan


@inject
@dataclass
class MemberRepositoryImpl:
    member_db_gateway: repositories.MemberRepository
    giro_office: GiroOffice
    plan_repository: repositories.PlanRepository

    def get_by_id(self, member_id: UUID) -> Optional[Member]:
        member = self.member_db_gateway.get_by_id(member_id)
        if member is None:
            return None
        return MemberImpl(
            member=member,
            giro_office=self.giro_office,
            plan_repository=self.plan_repository,
        )


@dataclass
class MemberImpl:
    member: MemberEntity
    giro_office: GiroOffice
    plan_repository: repositories.PlanRepository

    def pay_for_product(self, plan: Plan, amount: int) -> TransactionReceipt:
        transaction = ConsumerProductTransaction(
            buyer=self.member,
            plan=plan,
            amount=amount,
        )
        return self.giro_office.conduct_consumer_transaction(transaction)

    def get_planning_information(self, plan_id: UUID) -> Optional[Plan]:
        return self.plan_repository.get_plan_by_id(plan_id)
