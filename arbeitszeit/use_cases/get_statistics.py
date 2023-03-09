from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Tuple

from arbeitszeit.entities import PayoutFactor
from arbeitszeit.repositories import (
    AccountRepository,
    CompanyRepository,
    CooperationRepository,
    DatabaseGateway,
    MemberRepository,
    PlanRepository,
)


@dataclass
class StatisticsResponse:
    registered_companies_count: int
    registered_members_count: int
    cooperations_count: int
    certificates_count: Decimal
    available_product: Decimal
    active_plans_count: int
    active_plans_public_count: int
    avg_timeframe: Decimal
    planned_work: Decimal
    planned_resources: Decimal
    planned_means: Decimal
    payout_factor: Optional[PayoutFactor]


@dataclass
class GetStatistics:
    company_repository: CompanyRepository
    member_repository: MemberRepository
    plan_repository: PlanRepository
    cooperation_respository: CooperationRepository
    account_respository: AccountRepository
    database: DatabaseGateway

    def __call__(self) -> StatisticsResponse:
        (
            certs_total,
            available_product,
        ) = self._count_certificates_and_available_product()
        active_plans = self.plan_repository.get_plans().that_are_active()
        planning_statistics = active_plans.get_statistics()
        return StatisticsResponse(
            registered_companies_count=len(self.company_repository.get_companies()),
            registered_members_count=len(self.member_repository.get_members()),
            cooperations_count=self.cooperation_respository.count_cooperations(),
            certificates_count=certs_total,
            available_product=available_product,
            active_plans_count=len(active_plans),
            active_plans_public_count=len(active_plans.that_are_public()),
            avg_timeframe=planning_statistics.average_plan_duration_in_days,
            planned_work=planning_statistics.total_planned_costs.labour_cost,
            planned_resources=planning_statistics.total_planned_costs.resource_cost,
            planned_means=planning_statistics.total_planned_costs.means_cost,
            payout_factor=self.database.get_payout_factors()
            .ordered_by_calculation_date(descending=True)
            .first(),
        )

    def _count_certificates_and_available_product(self) -> Tuple[Decimal, Decimal]:
        """
        available certificates is sum of company work account balances and sum of member account balances
        """
        (
            certs_in_company_accounts,
            available_product,
        ) = self._count_certs_and_products_from_companies()

        certs_in_member_accounts = self._count_certs_in_member_accounts()
        certs_total = certs_in_company_accounts + certs_in_member_accounts
        return certs_total, available_product

    def _count_certs_and_products_from_companies(self) -> Tuple[Decimal, Decimal]:
        """available product is sum of prd account balances *(-1)"""
        certs_in_company_accounts = Decimal(0)
        available_product = Decimal(0)
        all_companies = self.company_repository.get_companies()
        for company in all_companies:
            available_product += self.account_respository.get_account_balance(
                company.product_account
            )
            certs_in_company_accounts += self.account_respository.get_account_balance(
                company.work_account
            )
        return certs_in_company_accounts, available_product * -1

    def _count_certs_in_member_accounts(self) -> Decimal:
        certs_in_member_accounts = Decimal(0)
        all_members = self.member_repository.get_members()
        for member in all_members:
            certs_in_member_accounts += self.account_respository.get_account_balance(
                member.account
            )
        return certs_in_member_accounts
