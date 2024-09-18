from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from arbeitszeit.use_cases import get_company_summary, get_member_dashboard


@dataclass
class AccountBalances:
    p_account: Decimal
    r_account: Decimal
    a_account: Decimal
    prd_account: Decimal


@dataclass
class BalanceChecker:
    get_company_summary: get_company_summary.GetCompanySummary
    get_member_dashboard_use_case: get_member_dashboard.GetMemberDashboardUseCase

    def get_company_account_balances(self, company: UUID) -> AccountBalances:
        response = self.get_company_summary(company_id=company)
        assert response
        return AccountBalances(
            p_account=response.account_balances.means,
            r_account=response.account_balances.raw_material,
            a_account=response.account_balances.work,
            prd_account=response.account_balances.product,
        )

    def get_member_account_balance(self, member: UUID) -> Decimal:
        request = get_member_dashboard.Request(member=member)
        response = self.get_member_dashboard_use_case.get_member_dashboard(
            request=request
        )
        return response.account_balance
