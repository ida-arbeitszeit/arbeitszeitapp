from arbeitszeit_flask.database.repositories import AccountRepository
from tests.data_generators import AccountGenerator, TransactionGenerator

from .flask import FlaskTestCase


class RepositoryTester(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.account_generator = self.injector.get(AccountGenerator)
        self.transaction_generator = self.injector.get(TransactionGenerator)
        self.repository = self.injector.get(AccountRepository)

    def test_the_account_balance_of_newly_created_accounts_is_0(self) -> None:
        account = self.account_generator.create_account()
        assert self.repository.get_account_balance(account) == 0

    def test_the_account_balance_of_accounts_equals_negative_sum_of_sent_transactions(
        self,
    ) -> None:
        account = self.account_generator.create_account()
        self.transaction_generator.create_transaction(
            sending_account=account, amount_sent=10
        )
        self.transaction_generator.create_transaction(
            sending_account=account, amount_sent=2.5
        )
        assert self.repository.get_account_balance(account) == -12.5

    def test_the_account_balance_of_accounts_equals_sum_of_received_transactions(
        self,
    ) -> None:
        account = self.account_generator.create_account()
        self.transaction_generator.create_transaction(
            receiving_account=account, amount_received=10
        )
        self.transaction_generator.create_transaction(
            receiving_account=account, amount_received=2.5
        )
        assert self.repository.get_account_balance(account) == 12.5

    def test_the_account_balance_of_accounts_reflects_sent_and_received_transactions(
        self,
    ) -> None:
        account = self.account_generator.create_account()
        self.transaction_generator.create_transaction(
            sending_account=account, amount_sent=10, amount_received=0
        )
        self.transaction_generator.create_transaction(
            receiving_account=account, amount_sent=0, amount_received=4
        )
        assert self.repository.get_account_balance(account) == -6

    def test_the_account_balance_is_zero_when_sending_and_receiving_account_of_transaction_are_the_same(
        self,
    ) -> None:
        account = self.account_generator.create_account()
        self.transaction_generator.create_transaction(
            sending_account=account,
            receiving_account=account,
            amount_sent=10,
            amount_received=10,
        )
        assert self.repository.get_account_balance(account) == 0
