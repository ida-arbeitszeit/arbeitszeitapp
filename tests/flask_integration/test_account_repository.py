from project.database.repositories import AccountRepository
from tests.data_generators import AccountGenerator, TransactionGenerator

from .dependency_injection import injection_test


@injection_test
def test_the_account_balance_of_newly_created_accounts_is_0(
    repository: AccountRepository,
    generator: AccountGenerator,
) -> None:
    account = generator.create_account()
    assert repository.get_account_balance(account) == 0


@injection_test
def test_the_account_balance_of_accounts_equals_negative_sum_of_sent_transactions(
    repository: AccountRepository,
    account_generator: AccountGenerator,
    transaction_generator: TransactionGenerator,
) -> None:
    account = account_generator.create_account()
    transaction_generator.create_transaction(sending_account=account, amount_sent=10)
    transaction_generator.create_transaction(sending_account=account, amount_sent=2.5)
    assert repository.get_account_balance(account) == -12.5


@injection_test
def test_the_account_balance_of_accounts_equals_sum_of_received_transactions(
    repository: AccountRepository,
    account_generator: AccountGenerator,
    transaction_generator: TransactionGenerator,
) -> None:
    account = account_generator.create_account()
    transaction_generator.create_transaction(
        receiving_account=account, amount_received=10
    )
    transaction_generator.create_transaction(
        receiving_account=account, amount_received=2.5
    )
    assert repository.get_account_balance(account) == 12.5


@injection_test
def test_the_account_balance_of_accounts_reflects_sent_and_received_transactions(
    repository: AccountRepository,
    account_generator: AccountGenerator,
    transaction_generator: TransactionGenerator,
) -> None:
    account = account_generator.create_account()
    transaction_generator.create_transaction(
        sending_account=account, amount_sent=10, amount_received=0
    )
    transaction_generator.create_transaction(
        receiving_account=account, amount_sent=0, amount_received=4
    )
    assert repository.get_account_balance(account) == -6


@injection_test
def test_the_account_balance_is_zero_when_sending_and_receiving_account_of_transaction_are_the_same(
    repository: AccountRepository,
    account_generator: AccountGenerator,
    transaction_generator: TransactionGenerator,
) -> None:
    account = account_generator.create_account()
    transaction_generator.create_transaction(
        sending_account=account,
        receiving_account=account,
        amount_sent=10,
        amount_received=10,
    )
    assert repository.get_account_balance(account) == 0
