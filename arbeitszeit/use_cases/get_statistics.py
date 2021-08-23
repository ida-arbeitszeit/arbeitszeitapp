from dataclasses import dataclass

from injector import inject

from arbeitszeit.repositories import CompanyRepository, MemberRepository, PlanRepository


@dataclass
class StatisticsResponse:
    registered_companies_count: int
    registered_members_count: int
    active_plans_count: int
    active_plans_public_count: int


@inject
@dataclass
class GetStatistics:
    company_repository: CompanyRepository
    member_repository: MemberRepository
    plan_repository: PlanRepository

    def __call__(self) -> StatisticsResponse:
        return StatisticsResponse(
            registered_companies_count=self.company_repository.count_registered_companies(),
            registered_members_count=self.member_repository.count_registered_members(),
            active_plans_count=self.plan_repository.count_active_plans(),
            active_plans_public_count=self.plan_repository.count_active_public_plans(),
        )
