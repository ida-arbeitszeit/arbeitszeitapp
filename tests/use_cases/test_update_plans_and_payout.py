from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID

from arbeitszeit.entities import AccountTypes, ProductionCosts
from arbeitszeit.use_cases import get_company_transactions, get_statistics
from arbeitszeit.use_cases.show_my_accounts import ShowMyAccounts, ShowMyAccountsRequest
from arbeitszeit.use_cases.update_plans_and_payout import UpdatePlansAndPayout
from tests.use_cases.base_test_case import BaseTestCase

from .dependency_injection import get_dependency_injector


class UseCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.injector = get_dependency_injector()
        self.payout = self.injector.get(UpdatePlansAndPayout)
        self.show_my_accounts = self.injector.get(ShowMyAccounts)
        self.get_company_transactions = self.injector.get(
            get_company_transactions.GetCompanyTransactions
        )
        self.get_statistics = self.injector.get(get_statistics.GetStatistics)

    def test_that_plan_with_requested_cooperation_has_no_requested_cooperation_after_expiration(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        requested_coop = self.cooperation_generator.create_cooperation()
        plan = self.plan_generator.create_plan(
            timeframe=5,
            requested_cooperation=requested_coop,
        )
        assert plan.requested_cooperation
        self.datetime_service.freeze_time(datetime(2000, 1, 11))
        self.payout()
        assert not plan.requested_cooperation

    def test_that_cooperating_plan_is_not_cooperating_after_expiration(self) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        cooperation = self.cooperation_generator.create_cooperation()
        plan = self.plan_generator.create_plan(
            timeframe=5,
            cooperation=cooperation,
        )
        assert plan.cooperation
        self.datetime_service.freeze_time(datetime(2000, 1, 11))
        self.payout()
        assert not plan.cooperation

    def test_that_payout_factor_ignores_plan_that_has_recently_expired(
        self,
    ) -> None:
        """The premise of this test is that we have a big public plan
        in the past and another productive plan that starts after the
        first public plan has expired.  We test for the fact that The
        labour certificate payout factor should be exactly 1 for the
        productive plan since there are no public plans at the same
        time.
        """
        expected_balance = Decimal(10)
        self.datetime_service.freeze_time(datetime(2020, 1, 1))
        self.plan_generator.create_plan(
            approved=True,
            is_public_service=True,
            timeframe=1,
            costs=ProductionCosts(Decimal(10), Decimal(10), Decimal(10)),
        )
        self.datetime_service.advance_time(timedelta(days=2))
        planner = self.company_generator.create_company()
        self.plan_generator.create_plan(
            is_public_service=False,
            timeframe=1,
            costs=ProductionCosts(
                means_cost=Decimal(0),
                resource_cost=Decimal(0),
                labour_cost=expected_balance,
            ),
            planner=planner,
        )
        self.datetime_service.advance_time(timedelta(days=1))
        self.payout()
        stats = self.get_statistics()
        assert stats.payout_factor
        assert stats.payout_factor.value == Decimal(1)

    def get_company_work_account_balance(self, company: UUID) -> Decimal:
        show_my_accounts_response = self.show_my_accounts(
            ShowMyAccountsRequest(company)
        )
        return show_my_accounts_response.balances[2]

    def count_transactions_of_type_a(self, company: UUID) -> int:
        response = self.get_company_transactions(company)
        return len(
            [
                transaction
                for transaction in response.transactions
                if self._transaction_received_on_a_account(transaction)
            ]
        )

    def _transaction_received_on_a_account(
        self, transaction: get_company_transactions.TransactionInfo
    ) -> bool:
        return transaction.account_type == AccountTypes.a
