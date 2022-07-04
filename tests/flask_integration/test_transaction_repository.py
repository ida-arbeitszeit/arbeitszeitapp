from datetime import datetime
from decimal import Decimal

from arbeitszeit_flask.database.repositories import TransactionRepository
from tests.data_generators import AccountGenerator, PlanGenerator

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
        amount_sent=Decimal(1),
        amount_received=Decimal(1),
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
        amount_sent=Decimal(1),
        amount_received=Decimal(1),
        purpose="test purpose",
    )
    assert repository.all_transactions_sent_by_account(sender_account) == [transaction]


@injection_test
def test_correct_sales_balance_of_plan_gets_returned_after_one_transaction(
    repository: TransactionRepository,
    account_generator: AccountGenerator,
    plan_generator: PlanGenerator,
) -> None:
    plan = plan_generator.create_plan()
    sender_account = account_generator.create_account()
    receiver_account = plan.planner.product_account
    repository.create_transaction(
        datetime.now(),
        sending_account=sender_account,
        receiving_account=receiver_account,
        amount_sent=Decimal(12),
        amount_received=Decimal(10),
        purpose=f"test {plan.id} test",
    )
    assert repository.get_sales_balance_of_plan(plan) == Decimal(10)


@injection_test
def test_correct_sales_balance_of_plan_gets_returned_after_two_transactions(
    repository: TransactionRepository,
    account_generator: AccountGenerator,
    plan_generator: PlanGenerator,
) -> None:
    plan = plan_generator.create_plan()
    sender_account_1 = account_generator.create_account()
    sender_account_2 = account_generator.create_account()
    receiver_account = plan.planner.product_account
    repository.create_transaction(
        datetime.now(),
        sending_account=sender_account_1,
        receiving_account=receiver_account,
        amount_sent=Decimal(12),
        amount_received=Decimal(10),
        purpose=f"test {plan.id} test",
    )
    repository.create_transaction(
        datetime.now(),
        sending_account=sender_account_2,
        receiving_account=receiver_account,
        amount_sent=Decimal(12),
        amount_received=Decimal(15),
        purpose=f"test2 {plan.id} test2",
    )
    assert repository.get_sales_balance_of_plan(plan) == Decimal(25)
