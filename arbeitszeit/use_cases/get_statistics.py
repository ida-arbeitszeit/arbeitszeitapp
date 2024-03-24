from dataclasses import dataclass
from decimal import Decimal

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.payout_factor import PayoutFactorService
from arbeitszeit.fpc_balance import PublicFundService
from arbeitszeit.repositories import AccountResult, DatabaseGateway


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
    payout_factor: Decimal
    fpc_balance: Decimal


@dataclass
class GetStatistics:
    database: DatabaseGateway
    datetime_service: DatetimeService
    fic_service: PayoutFactorService
    fpc_service: PublicFundService

    def __call__(self) -> StatisticsResponse:
        fic = self.fic_service.get_current_payout_factor()
        fpc_balance = self.fpc_service.get_current_fpc_balance()
        certs_total = self._estimate_total_certificates(fic)
        available_product = self._estimate_available_product()
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
            payout_factor=fic,
            fpc_balance=fpc_balance,
        )

    def _estimate_total_certificates(self, fic: Decimal) -> Decimal:
        return (
            self._count_certs_in_member_accounts()
            + _sum_account_balances(
                self.database.get_accounts().that_are_labour_accounts()
            )
            * fic
        )

    def _estimate_available_product(self) -> Decimal:
        return (
            _sum_account_balances(
                self.database.get_accounts().that_are_product_accounts()
            )
            * -1
        )

    def _count_certs_in_member_accounts(self) -> Decimal:
        return _sum_account_balances(
            self.database.get_accounts().that_are_member_accounts()
        )


def _sum_account_balances(accounts: AccountResult) -> Decimal:
    return sum(
        (balance for (_, balance) in accounts.joined_with_balance()),
        Decimal(0),
    )
