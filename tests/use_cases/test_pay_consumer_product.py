from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

import pytest

from arbeitszeit import errors
from arbeitszeit.entities import PurposesOfPurchases
from arbeitszeit.use_cases import PayConsumerProduct
from tests.data_generators import MemberGenerator, PlanGenerator
from tests.datetime_service import FakeDatetimeService

from .dependency_injection import injection_test
from .repositories import AccountRepository, PurchaseRepository, TransactionRepository


@injection_test
def test_error_is_raised_if_plan_is_not_active_yet(
    pay_consumer_product: PayConsumerProduct,
    member_generator: MemberGenerator,
    plan_generator: PlanGenerator,
):
    sender = member_generator.create_member()
    plan = plan_generator.create_plan()
    pieces = 3
    with pytest.raises(errors.PlanIsInactive):
        pay_consumer_product(make_request(sender.id, plan.id, pieces))


@injection_test
def test_error_is_raised_if_plan_is_expired(
    pay_consumer_product: PayConsumerProduct,
    member_generator: MemberGenerator,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
    sender = member_generator.create_member()
    plan = plan_generator.create_plan(
        plan_creation_date=datetime_service.now_minus_ten_days(),
        timeframe=1,
    )
    pieces = 3
    plan.expired = True
    with pytest.raises(errors.PlanIsInactive):
        pay_consumer_product(make_request(sender.id, plan.id, pieces))


@injection_test
def test_that_correct_transaction_is_added(
    pay_consumer_product: PayConsumerProduct,
    member_generator: MemberGenerator,
    plan_generator: PlanGenerator,
    transaction_repository: TransactionRepository,
    datetime_service: FakeDatetimeService,
):
    sender = member_generator.create_member()
    plan = plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day()
    )
    pieces = 3
    pay_consumer_product(make_request(sender.id, plan.id, pieces))
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
    datetime_service: FakeDatetimeService,
):
    sender = member_generator.create_member()
    plan = plan_generator.create_plan(
        is_public_service=True, activation_date=datetime_service.now_minus_one_day()
    )
    pieces = 3
    pay_consumer_product(make_request(sender.id, plan.id, pieces))
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
    datetime_service: FakeDatetimeService,
):
    sender = member_generator.create_member()
    plan = plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day()
    )
    pieces = 3
    pay_consumer_product(make_request(sender.id, plan.id, pieces))
    costs = pieces * plan.price_per_unit()
    assert account_repository.get_account_balance(sender.account) == -costs
    assert account_repository.get_account_balance(plan.planner.product_account) == costs


@injection_test
def test_balances_are_adjusted_correctly_when_plan_is_public_service(
    pay_consumer_product: PayConsumerProduct,
    member_generator: MemberGenerator,
    plan_generator: PlanGenerator,
    account_repository: AccountRepository,
    datetime_service: FakeDatetimeService,
):
    sender = member_generator.create_member()
    plan = plan_generator.create_plan(
        is_public_service=True, activation_date=datetime_service.now_minus_one_day()
    )
    pieces = 3
    pay_consumer_product(make_request(sender.id, plan.id, pieces))
    costs = pieces * plan.price_per_unit()
    assert account_repository.get_account_balance(sender.account) == -costs
    assert account_repository.get_account_balance(plan.planner.product_account) == costs


@injection_test
def test_correct_purchase_is_added(
    pay_consumer_product: PayConsumerProduct,
    member_generator: MemberGenerator,
    plan_generator: PlanGenerator,
    purchase_repository: PurchaseRepository,
    datetime_service: FakeDatetimeService,
):
    sender = member_generator.create_member()
    plan = plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day()
    )
    pieces = 3
    pay_consumer_product(make_request(sender.id, plan.id, pieces))
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
    datetime_service: FakeDatetimeService,
):
    sender = member_generator.create_member()
    plan = plan_generator.create_plan(
        is_public_service=True, activation_date=datetime_service.now_minus_one_day()
    )
    pieces = 3
    pay_consumer_product(make_request(sender.id, plan.id, pieces))
    assert len(purchase_repository.purchases) == 1
    purchase_added = purchase_repository.purchases[0]
    assert purchase_added.price_per_unit == 0
    assert purchase_added.plan == plan


def make_request(
    buyer: UUID, plan: UUID, amount: int
) -> PayConsumerProductRequestTestImpl:
    return PayConsumerProductRequestTestImpl(
        buyer=buyer,
        plan=plan,
        amount=amount,
    )


@dataclass
class PayConsumerProductRequestTestImpl:
    buyer: UUID
    plan: UUID
    amount: int

    def get_amount(self) -> int:
        return self.amount

    def get_plan_id(self) -> UUID:
        return self.plan

    def get_buyer_id(self) -> UUID:
        return self.buyer
