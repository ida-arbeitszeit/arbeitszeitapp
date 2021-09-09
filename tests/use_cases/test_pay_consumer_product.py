import pytest

from arbeitszeit import errors
from arbeitszeit.entities import PurposesOfPurchases
from arbeitszeit.use_cases import PayConsumerProduct
from tests.data_generators import MemberGenerator, PlanGenerator
from tests.datetime_service import FakeDatetimeService

from .dependency_injection import injection_test
from .repositories import AccountRepository, PurchaseRepository, TransactionRepository


@injection_test
def test_error_is_raised_if_plan_is_expired(
    pay_consumer_product: PayConsumerProduct,
    member_generator: MemberGenerator,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
    sender = member_generator.create_member()
    plan = plan_generator.create_plan(
        plan_creation_date=datetime_service.now_minus_two_days,
        timeframe=1,
    )
    pieces = 3
    plan.expired = True
    with pytest.raises(errors.PlanIsExpired):
        pay_consumer_product(sender, plan, pieces)


@injection_test
def test_that_correct_transaction_is_added(
    pay_consumer_product: PayConsumerProduct,
    member_generator: MemberGenerator,
    plan_generator: PlanGenerator,
    transaction_repository: TransactionRepository,
):
    sender = member_generator.create_member()
    plan = plan_generator.create_plan()
    pieces = 3
    pay_consumer_product(sender, plan, pieces)
    assert len(transaction_repository.transactions) == 1
    transaction_added = transaction_repository.transactions[0]
    expected_amount = pieces * plan.price_per_unit()
    assert transaction_added.sending_account == sender.account
    assert transaction_added.receiving_account == plan.planner.product_account
    assert transaction_added.amount == expected_amount


@injection_test
def test_that_correct_transaction_is_added_when_plan_is_public_service(
    pay_consumer_product: PayConsumerProduct,
    member_generator: MemberGenerator,
    plan_generator: PlanGenerator,
    transaction_repository: TransactionRepository,
):
    sender = member_generator.create_member()
    plan = plan_generator.create_plan(is_public_service=True)
    pieces = 3
    pay_consumer_product(sender, plan, pieces)
    assert len(transaction_repository.transactions) == 1
    transaction_added = transaction_repository.transactions[0]
    expected_amount = 0
    assert transaction_added.sending_account == sender.account
    assert transaction_added.receiving_account == plan.planner.product_account
    assert transaction_added.amount == expected_amount


@injection_test
def test_balances_are_adjusted_correctly(
    pay_consumer_product: PayConsumerProduct,
    member_generator: MemberGenerator,
    plan_generator: PlanGenerator,
    account_repository: AccountRepository,
):
    sender = member_generator.create_member()
    plan = plan_generator.create_plan()
    pieces = 3
    pay_consumer_product(sender, plan, pieces)
    costs = pieces * plan.price_per_unit()
    assert account_repository.get_account_balance(sender.account) == -costs
    assert account_repository.get_account_balance(plan.planner.product_account) == costs


@injection_test
def test_balances_are_adjusted_correctly_when_plan_is_public_service(
    pay_consumer_product: PayConsumerProduct,
    member_generator: MemberGenerator,
    plan_generator: PlanGenerator,
    account_repository: AccountRepository,
):
    sender = member_generator.create_member()
    plan = plan_generator.create_plan(is_public_service=True)
    pieces = 3
    pay_consumer_product(sender, plan, pieces)
    costs = pieces * plan.price_per_unit()
    assert account_repository.get_account_balance(sender.account) == -costs
    assert account_repository.get_account_balance(plan.planner.product_account) == costs


@injection_test
def test_correct_purchase_is_added(
    pay_consumer_product: PayConsumerProduct,
    member_generator: MemberGenerator,
    plan_generator: PlanGenerator,
    purchase_repository: PurchaseRepository,
):
    sender = member_generator.create_member()
    plan = plan_generator.create_plan()
    pieces = 3
    pay_consumer_product(sender, plan, pieces)
    assert len(purchase_repository.purchases) == 1
    purchase_added = purchase_repository.purchases[0]
    assert purchase_added.price_per_unit == plan.price_per_unit()
    assert purchase_added.amount == pieces
    assert purchase_added.purpose == PurposesOfPurchases.consumption
    assert purchase_added.buyer == sender
    assert purchase_added.plan == plan


@injection_test
def test_correct_purchase_is_added_when_plan_is_public_service(
    pay_consumer_product: PayConsumerProduct,
    member_generator: MemberGenerator,
    plan_generator: PlanGenerator,
    purchase_repository: PurchaseRepository,
):
    sender = member_generator.create_member()
    plan = plan_generator.create_plan(is_public_service=True)
    pieces = 3
    pay_consumer_product(sender, plan, pieces)
    assert len(purchase_repository.purchases) == 1
    purchase_added = purchase_repository.purchases[0]
    assert purchase_added.price_per_unit == 0
    assert purchase_added.plan == plan
