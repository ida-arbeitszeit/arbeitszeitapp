from dataclasses import dataclass
from decimal import Decimal
from typing import List
from uuid import UUID

from injector import inject

from arbeitszeit.repositories import (
    AccountRepository,
    CompanyWorkerRepository,
    MemberRepository,
)


@dataclass
class Workplace:
    workplace_name: str
    workplace_email: str


@dataclass
class GetMemberProfileInfoResponse:
    workplaces: List[Workplace]
    account_balance: Decimal
    name: str
    email: str
    id: UUID


@inject
@dataclass
class GetMemberProfileInfo:
    company_worker_repository: CompanyWorkerRepository
    account_repository: AccountRepository
    member_repository: MemberRepository

    def __call__(self, member: UUID) -> GetMemberProfileInfoResponse:
        _member = self.member_repository.get_by_id(member)
        workplaces = [
            Workplace(
                workplace_name=workplace.name,
                workplace_email=workplace.email,
            )
            for workplace in self.company_worker_repository.get_member_workplaces(
                member
            )
        ]
        return GetMemberProfileInfoResponse(
            workplaces=workplaces,
            account_balance=self.account_repository.get_account_balance(
                _member.account
            ),
            name=_member.name,
            email=_member.email,
            id=_member.id,
        )
