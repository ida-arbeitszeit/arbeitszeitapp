from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Tuple

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import PayoutFactor
from arbeitszeit.payout_factor import PayoutFactorService
from arbeitszeit.repositories import AccountRepository, DatabaseGateway


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
    account_repository: AccountRepository
    database: DatabaseGateway
    datetime_service: DatetimeService
    fic_service: PayoutFactorService

    def __call__(self) -> StatisticsResponse:
        (
            certs_total,
            available_product,
        ) = self._count_certificates_and_available_product()
        now = self.datetime_service.now()
        active_plans = (
            self.database.get_plans()
            .that_will_expire_after(now)
            .that_were_activated_before(now)
        )
        planning_statistics = active_plans.get_statistics()
        return StatisticsResponse(
            registered_companies_count=len(self.database.get_companies()),
            registered_members_count=len(self.database.get_members()),
            cooperations_count=len(self.database.get_cooperations()),
            certificates_count=certs_total,
            available_product=available_product,
            active_plans_count=len(active_plans),
            active_plans_public_count=len(active_plans.that_are_public()),
            avg_timeframe=planning_statistics.average_plan_duration_in_days,
            planned_work=planning_statistics.total_planned_costs.labour_cost,
            planned_resources=planning_statistics.total_planned_costs.resource_cost,
            planned_means=planning_statistics.total_planned_costs.means_cost,
            payout_factor=self.fic_service.get_current_payout_factor(),
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
        all_companies = self.database.get_companies()
        for company in all_companies:
            available_product += self.account_repository.get_account_balance(
                company.product_account
            )
            certs_in_company_accounts += self.account_repository.get_account_balance(
                company.work_account
            )
        return certs_in_company_accounts, available_product * -1

    def _count_certs_in_member_accounts(self) -> Decimal:
        certs_in_member_accounts = Decimal(0)
        all_members = self.database.get_members()
        for member in all_members:
            certs_in_member_accounts += self.account_repository.get_account_balance(
                member.account
            )
        return certs_in_member_accounts
