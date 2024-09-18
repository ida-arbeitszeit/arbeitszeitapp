from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.records import CompanyWorkInvite
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class Request:
    member: UUID


@dataclass
class Workplace:
    workplace_name: str
    workplace_id: UUID


@dataclass
class WorkInvitation:
    invite_id: UUID
    company_id: UUID
    company_name: str


@dataclass
class PlanDetails:
    plan_id: UUID
    prd_name: str
    activation_date: datetime


@dataclass
class Response:
    workplaces: List[Workplace]
    invites: List[WorkInvitation]
    three_latest_plans: List[PlanDetails]
    account_balance: Decimal
    name: str
    email: str
    id: UUID


@dataclass
class GetMemberDashboardUseCase:
    database_gateway: DatabaseGateway
    datetime_service: DatetimeService

    def get_member_dashboard(self, request: Request) -> Response:
        record = (
            self.database_gateway.get_members()
            .with_id(request.member)
            .joined_with_email_address()
            .first()
        )
        assert record
        _member, email = record
        return Response(
            workplaces=self._get_workplaces(request.member),
            invites=self._get_invites(request.member),
            three_latest_plans=self._get_three_latest_plans(),
            account_balance=self._get_account_balance(request.member),
            name=_member.name,
            email=email.address,
            id=_member.id,
        )

    def _get_account_balance(self, member: UUID) -> Decimal:
        result = (
            self.database_gateway.get_accounts()
            .owned_by_member(member)
            .joined_with_balance()
            .first()
        )
        assert result
        return result[1]

    def _get_three_latest_plans(self) -> List[PlanDetails]:
        now = self.datetime_service.now()
        latest_plans = (
            self.database_gateway.get_plans()
            .that_will_expire_after(now)
            .that_were_activated_before(now)
            .ordered_by_creation_date(ascending=False)
            .limit(3)
        )
        plans = []
        for plan in latest_plans:
            assert plan.activation_date
            plans.append(PlanDetails(plan.id, plan.prd_name, plan.activation_date))
        return plans

    def _get_workplaces(self, member: UUID) -> List[Workplace]:
        return [
            Workplace(
                workplace_name=company.name,
                workplace_id=company.id,
            )
            for company in self.database_gateway.get_companies().that_are_workplace_of_member(
                member
            )
        ]

    def _get_invites(self, member: UUID) -> List[WorkInvitation]:
        return [
            self._render_company_work_invite(invite)
            for invite in self.database_gateway.get_company_work_invites().addressing(
                member
            )
        ]

    def _render_company_work_invite(self, invite: CompanyWorkInvite) -> WorkInvitation:
        company = self.database_gateway.get_companies().with_id(invite.company).first()
        assert company
        return WorkInvitation(
            invite_id=invite.id,
            company_id=invite.company,
            company_name=company.name,
        )
