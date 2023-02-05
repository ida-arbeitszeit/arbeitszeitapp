from uuid import uuid4

from arbeitszeit_flask.database.repositories import AccountRepository
from tests.data_generators import AccountGenerator, TransactionGenerator

from .flask import FlaskTestCase


class RepositoryTester(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.account_generator: AccountGenerator = self.injector.get(AccountGenerator)
        self.transaction_generator: TransactionGenerator = self.injector.get(
            TransactionGenerator
        )
        self.repository: AccountRepository = self.injector.get(AccountRepository)

    def test_the_account_balance_of_newly_created_accounts_is_0(self) -> None:
        account = self.account_generator.create_account()
        assert self.repository.get_account_balance(account.id) == 0

    def test_the_account_balance_of_accounts_equals_negative_sum_of_sent_transactions(
        self,
    ) -> None:
        account = self.account_generator.create_account()
        self.transaction_generator.create_transaction(
            sending_account=account.id, amount_sent=10
        )
        self.transaction_generator.create_transaction(
            sending_account=account.id, amount_sent=2.5
        )
        assert self.repository.get_account_balance(account.id) == -12.5

    def test_the_account_balance_of_accounts_equals_sum_of_received_transactions(
        self,
    ) -> None:
        account = self.account_generator.create_account()
        self.transaction_generator.create_transaction(
            receiving_account=account.id, amount_received=10
        )
        self.transaction_generator.create_transaction(
            receiving_account=account.id, amount_received=2.5
        )
        assert self.repository.get_account_balance(account.id) == 12.5

    def test_the_account_balance_of_accounts_reflects_sent_and_received_transactions(
        self,
    ) -> None:
        account = self.account_generator.create_account()
        self.transaction_generator.create_transaction(
            sending_account=account.id, amount_sent=10, amount_received=0
        )
        self.transaction_generator.create_transaction(
            receiving_account=account.id, amount_sent=0, amount_received=4
        )
        assert self.repository.get_account_balance(account.id) == -6

    def test_the_account_balance_is_zero_when_sending_and_receiving_account_of_transaction_are_the_same(
        self,
    ) -> None:
        account = self.account_generator.create_account()
        self.transaction_generator.create_transaction(
            sending_account=account.id,
            receiving_account=account.id,
            amount_sent=10,
            amount_received=10,
        )
        assert self.repository.get_account_balance(account.id) == 0

    def test_that_a_priori_no_accounts_can_be_queried(self) -> None:
        print(list(self.repository.get_accounts()))
        assert not self.repository.get_accounts()

    def test_there_are_accounts_to_be_queried_when_one_was_created(self) -> None:
        self.account_generator.create_account()
        assert self.repository.get_accounts()

    def test_only_include_relevant_account_when_filtering_by_id(self) -> None:
        random_id = uuid4()
        actual_id = self.account_generator.create_account().id
        assert not self.repository.get_accounts().with_id(random_id)
        assert self.repository.get_accounts().with_id(actual_id)
