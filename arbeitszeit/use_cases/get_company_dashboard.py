from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.repositories import (
    CompanyRepository,
    DatabaseGateway,
    MemberRepository,
)


@dataclass
class GetCompanyDashboardUseCase:
    class Failure(Exception):
        pass

    @dataclass
    class Response:
        @dataclass
        class LatestPlansDetails:
            plan_id: UUID
            prd_name: str
            activation_date: datetime

        @dataclass
        class CompanyInfo:
            id: UUID
            name: str
            email: str

        company_info: CompanyInfo
        has_workers: bool
        three_latest_plans: List[LatestPlansDetails]

    company_repository: CompanyRepository
    member_repository: MemberRepository
    database_gateway: DatabaseGateway
    datetime_service: DatetimeService

    def get_dashboard(self, company_id: UUID) -> Response:
        company = self.company_repository.get_companies().with_id(company_id).first()
        if company is None:
            raise self.Failure()
        company_info = self.Response.CompanyInfo(
            id=company.id, name=company.name, email=company.email
        )
        has_workers = bool(
            self.member_repository.get_members().working_at_company(company_id)
        )
        three_latest_plans = self._get_three_latest_plans()
        return self.Response(
            company_info=company_info,
            has_workers=has_workers,
            three_latest_plans=three_latest_plans,
        )

    def _get_three_latest_plans(self) -> List[Response.LatestPlansDetails]:
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
            plans.append(
                self.Response.LatestPlansDetails(
                    plan.id, plan.prd_name, plan.activation_date
                )
            )
        return plans
