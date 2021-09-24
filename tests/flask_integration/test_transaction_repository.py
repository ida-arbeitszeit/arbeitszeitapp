from datetime import datetime
from decimal import Decimal

from project.database.repositories import TransactionRepository
from tests.data_generators import AccountGenerator

from .dependency_injection import injection_test


@injection_test
def test_created_transactions_show_up_in_all_transactions_received_by_account(
    repository: TransactionRepository,
    account_generator: AccountGenerator,
) -> None:
    sender_account = account_generator.create_account()
    receiver_account = account_generator.create_account()
    transaction = repository.create_transaction(
        datetime.now(),
        sending_account=sender_account,
        receiving_account=receiver_account,
        amount=Decimal(1),
        purpose="test purpose",
    )
    assert repository.all_transactions_received_by_account(receiver_account) == [
        transaction
    ]


@injection_test
def test_created_transactions_show_up_in_all_sent_received_by_account(
    repository: TransactionRepository,
    account_generator: AccountGenerator,
) -> None:
    sender_account = account_generator.create_account()
    receiver_account = account_generator.create_account()
    transaction = repository.create_transaction(
        datetime.now(),
        sending_account=sender_account,
        receiving_account=receiver_account,
        amount=Decimal(1),
        purpose="test purpose",
    )
    assert repository.all_transactions_sent_by_account(sender_account) == [transaction]
