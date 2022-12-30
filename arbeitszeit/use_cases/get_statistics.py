from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Tuple

from injector import inject

from arbeitszeit.entities import PayoutFactor
from arbeitszeit.repositories import (
    AccountRepository,
    CompanyRepository,
    CooperationRepository,
    MemberRepository,
    PayoutFactorRepository,
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


@inject
@dataclass
class GetStatistics:
    company_repository: CompanyRepository
    member_repository: MemberRepository
    plan_repository: PlanRepository
    cooperation_respository: CooperationRepository
    account_respository: AccountRepository
    payout_factor_repository: PayoutFactorRepository

    def __call__(self) -> StatisticsResponse:
        (
            certs_total,
            available_product,
        ) = self._count_certificates_and_available_product()
        return StatisticsResponse(
            registered_companies_count=len(self.company_repository.get_companies()),
            registered_members_count=len(self.member_repository.get_members()),
            cooperations_count=self.cooperation_respository.count_cooperations(),
            certificates_count=certs_total,
            available_product=available_product,
            active_plans_count=len(self.plan_repository.get_active_plans()),
            active_plans_public_count=len(
                self.plan_repository.get_active_plans().that_are_public()
            ),
            avg_timeframe=self.plan_repository.avg_timeframe_of_active_plans(),
            planned_work=self.plan_repository.sum_of_active_planned_work(),
            planned_resources=self.plan_repository.sum_of_active_planned_resources(),
            planned_means=self.plan_repository.sum_of_active_planned_means(),
            payout_factor=self.payout_factor_repository.get_latest_payout_factor(),
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
