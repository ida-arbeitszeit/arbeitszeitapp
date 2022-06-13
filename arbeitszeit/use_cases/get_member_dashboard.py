from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List
from uuid import UUID

from injector import inject

from arbeitszeit.repositories import (
    AccountRepository,
    CompanyWorkerRepository,
    MemberRepository,
    PlanRepository,
)


@dataclass
class Workplace:
    workplace_name: str
    workplace_email: str


@dataclass
class PlanDetails:
    plan_id: UUID
    prd_name: str
    activation_date: datetime


@dataclass
class GetMemberDashboardResponse:
    workplaces: List[Workplace]
    three_latest_plans: List[PlanDetails]
    account_balance: Decimal
    name: str
    email: str
    id: UUID


@inject
@dataclass
class GetMemberDashboard:
    company_worker_repository: CompanyWorkerRepository
    account_repository: AccountRepository
    member_repository: MemberRepository
    plan_repository: PlanRepository

    def __call__(self, member: UUID) -> GetMemberDashboardResponse:
        _member = self.member_repository.get_by_id(member)
        assert _member is not None
        workplaces = [
            Workplace(
                workplace_name=workplace.name,
                workplace_email=workplace.email,
            )
            for workplace in self.company_worker_repository.get_member_workplaces(
                member
            )
        ]
        return GetMemberDashboardResponse(
            workplaces=workplaces,
            three_latest_plans=self._get_three_latest_plans(),
            account_balance=self.account_repository.get_account_balance(
                _member.account
            ),
            name=_member.name,
            email=_member.email,
            id=_member.id,
        )

    def _get_three_latest_plans(self) -> List[PlanDetails]:
        latest_plans = (
            self.plan_repository.get_three_latest_active_plans_ordered_by_activation_date()
        )
        plans = []
        for plan in latest_plans:
            assert plan.activation_date
            plans.append(PlanDetails(plan.id, plan.prd_name, plan.activation_date))
        return plans
