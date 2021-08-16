import pytest

from arbeitszeit import errors
from arbeitszeit.use_cases import PayConsumerProduct

from .data_generators import CompanyGenerator, MemberGenerator, PlanGenerator
from .datetime_service import FakeDatetimeService
from .dependency_injection import injection_test
from .repositories import AccountRepository, TransactionRepository


@injection_test
def test_error_is_raised_if_company_is_not_planner(
    pay_consumer_product: PayConsumerProduct,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
):
    sender = member_generator.create_member()
    receiver = company_generator.create_company()
    planner = company_generator.create_company()
    plan = plan_generator.create_plan(planner=planner)
    pieces = 3
    with pytest.raises(errors.CompanyIsNotPlanner):
        pay_consumer_product(sender, receiver, plan, pieces)


@injection_test
def test_error_is_raised_if_plan_is_expired(
    pay_consumer_product: PayConsumerProduct,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
    sender = member_generator.create_member()
    receiver = company_generator.create_company()
    plan = plan_generator.create_plan(
        plan_creation_date=datetime_service.now_minus_two_days,
        timeframe=1,
        planner=receiver,
    )
    pieces = 3
    plan.expired = True
    with pytest.raises(errors.PlanIsExpired):
        pay_consumer_product(sender, receiver, plan, pieces)


@injection_test
def test_that_correct_transaction_is_added(
    pay_consumer_product: PayConsumerProduct,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
    transaction_repository: TransactionRepository,
):
    sender = member_generator.create_member()
    receiver = company_generator.create_company()
    plan = plan_generator.create_plan(planner=receiver)
    pieces = 3
    pay_consumer_product(sender, receiver, plan, pieces)
    assert len(transaction_repository.transactions) == 1
    transaction_added = transaction_repository.transactions[0]
    expected_amount = pieces * plan.price_per_unit()
    assert transaction_added.account_from == sender.account
    assert transaction_added.account_to == receiver.product_account
    assert transaction_added.amount == expected_amount


@injection_test
def test_that_correct_transaction_is_added_when_plan_is_public_service(
    pay_consumer_product: PayConsumerProduct,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
    transaction_repository: TransactionRepository,
):
    sender = member_generator.create_member()
    receiver = company_generator.create_company()
    plan = plan_generator.create_plan(planner=receiver, is_public_service=True)
    pieces = 3
    pay_consumer_product(sender, receiver, plan, pieces)
    assert len(transaction_repository.transactions) == 1
    transaction_added = transaction_repository.transactions[0]
    expected_amount = pieces * plan.price_per_unit()
    assert transaction_added.account_from == sender.account
    assert transaction_added.account_to == receiver.product_account
    assert transaction_added.amount == expected_amount


@injection_test
def test_balances_are_adjusted_correctly(
    pay_consumer_product: PayConsumerProduct,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
    account_repository: AccountRepository,
):
    sender = member_generator.create_member()
    receiver = company_generator.create_company()
    plan = plan_generator.create_plan(planner=receiver)
    pieces = 3
    pay_consumer_product(sender, receiver, plan, pieces)
    costs = pieces * plan.price_per_unit()
    assert account_repository.get_account_balance(sender.account) == -costs
    assert account_repository.get_account_balance(receiver.product_account) == costs


@injection_test
def test_balances_are_adjusted_correctly_when_plan_is_public_service(
    pay_consumer_product: PayConsumerProduct,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
    account_repository: AccountRepository,
):
    sender = member_generator.create_member()
    receiver = company_generator.create_company()
    plan = plan_generator.create_plan(planner=receiver, is_public_service=True)
    pieces = 3
    pay_consumer_product(sender, receiver, plan, pieces)
    costs = pieces * plan.price_per_unit()
    assert account_repository.get_account_balance(sender.account) == -costs
    assert account_repository.get_account_balance(receiver.product_account) == costs
