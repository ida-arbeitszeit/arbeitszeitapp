from dataclasses import dataclass
from decimal import Decimal

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.decimal import decimal_sum
from arbeitszeit.repositories import AccountResult, DatabaseGateway
from arbeitszeit.services.payout_factor import PayoutFactorService
from arbeitszeit.services.psf_balance import PublicSectorFundService


@dataclass
class StatisticsResponse:
    registered_companies_count: int
    registered_members_count: int
    cooperations_count: int
    certificates_count: Decimal
    available_product_in_productive_sector: Decimal
    active_plans_count: int
    active_plans_public_count: int
    avg_timeframe: Decimal
    planned_work: Decimal
    planned_resources: Decimal
    planned_means: Decimal
    payout_factor: Decimal
    psf_balance: Decimal


@dataclass
class GetStatisticsInteractor:
    database: DatabaseGateway
    datetime_service: DatetimeService
    fic_service: PayoutFactorService
    psf_service: PublicSectorFundService

    def get_statistics(self) -> StatisticsResponse:
        fic = self.fic_service.calculate_current_payout_factor()
        psf_balance = self.psf_service.calculate_psf_balance()
        now = self.datetime_service.now()
        active_plans = (
            self.database.get_plans()
            .that_will_expire_after(now)
            .that_were_approved_before(now)
        )
        planning_statistics = active_plans.get_statistics()
        return StatisticsResponse(
            registered_companies_count=len(self.database.get_companies()),
            registered_members_count=len(self.database.get_members()),
            cooperations_count=len(self.database.get_cooperations()),
            certificates_count=self._estimate_total_certificates(fic),
            available_product_in_productive_sector=self._available_product_in_productive_sector(),
            active_plans_count=len(active_plans),
            active_plans_public_count=len(active_plans.that_are_public()),
            avg_timeframe=planning_statistics.average_plan_duration_in_days,
            planned_work=planning_statistics.total_planned_costs.labour_cost,
            planned_resources=planning_statistics.total_planned_costs.resource_cost,
            planned_means=planning_statistics.total_planned_costs.means_cost,
            payout_factor=fic,
            psf_balance=psf_balance,
        )

    def _estimate_total_certificates(self, fic: Decimal) -> Decimal:
        """
        Estimated total number of certificates available in the economy.
        This is the sum of all certificates in member accounts and
        the certificates in company labour accounts multiplied by the
        current payout factor (fic).
        The certificates in member accounts are not multiplied by the
        current payout factor, because they have already been
        multiplied by the current payout factor when they were
        transferred to the member account.
        """
        certs = (
            self._count_certs_in_member_accounts()
            + self._count_certs_in_company_labour_accounts() * fic
        )
        return certs

    def _count_certs_in_member_accounts(self) -> Decimal:
        sum = _sum_account_balances(
            self.database.get_accounts().that_are_member_accounts()
        )
        return sum

    def _count_certs_in_company_labour_accounts(self) -> Decimal:
        return _sum_account_balances(
            self.database.get_accounts().that_are_labour_accounts()
        )

    def _available_product_in_productive_sector(self) -> Decimal:
        """
        The accumulated balances of prd accounts can be interpreted as
        the available product for productive or private consumption in the
        productive sector. It excludes products of the public sector.
        """
        available_product = (
            _sum_account_balances(
                self.database.get_accounts().that_are_product_accounts()
            )
            * -1
        )
        return available_product


def _sum_account_balances(accounts: AccountResult) -> Decimal:
    return decimal_sum(
        (balance for (_, balance) in accounts.joined_with_balance()),
    )
