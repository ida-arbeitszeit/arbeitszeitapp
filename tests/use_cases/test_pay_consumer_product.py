from __future__ import annotations

from dataclasses import dataclass
from unittest import TestCase
from uuid import UUID, uuid4

from arbeitszeit.entities import PurposesOfPurchases
from arbeitszeit.use_cases import PayConsumerProduct
from arbeitszeit.use_cases.pay_consumer_product import RejectionReason
from tests.data_generators import MemberGenerator, PlanGenerator
from tests.datetime_service import FakeDatetimeService

from .dependency_injection import get_dependency_injector
from .repositories import AccountRepository, PurchaseRepository, TransactionRepository


class PayConsumerProductTests(TestCase):
    def setUp(self):
        injector = get_dependency_injector()
        self.member_generator = injector.get(MemberGenerator)
        self.plan_generator = injector.get(PlanGenerator)
        self.pay_consumer_product = injector.get(PayConsumerProduct)
        self.datetime_service = injector.get(FakeDatetimeService)
        self.transaction_repository = injector.get(TransactionRepository)
        self.account_repository = injector.get(AccountRepository)
        self.purchase_repository = injector.get(PurchaseRepository)
        self.buyer = self.member_generator.create_member()

    def test_payment_fails_if_plan_isnt_active_yet(self):
        plan = self.plan_generator.create_plan()
        response = self.pay_consumer_product(self.make_request(plan.id, amount=3))
        self.assertFalse(response.is_accepted)

    def test_payment_is_unsuccessful_if_plan_is_expired(self):
        plan = self.plan_generator.create_plan(
            plan_creation_date=self.datetime_service.now_minus_ten_days(),
            timeframe=1,
        )
        plan.expired = True
        response = self.pay_consumer_product(self.make_request(plan.id, amount=3))
        self.assertFalse(response.is_accepted)

    def test_that_correct_transaction_is_added(self):
        plan = self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_one_day()
        )
        pieces = 3
        self.pay_consumer_product(self.make_request(plan.id, pieces))
        assert len(self.transaction_repository.transactions) == 1
        transaction_added = self.transaction_repository.transactions[0]
        expected_amount = pieces * plan.price_per_unit
        assert transaction_added.sending_account == self.buyer.account
        assert transaction_added.receiving_account == plan.planner.product_account
        assert transaction_added.amount == expected_amount

    def test_balances_are_adjusted_correctly(self) -> None:
        plan = self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_one_day()
        )
        pieces = 3
        self.pay_consumer_product(self.make_request(plan.id, pieces))
        costs = pieces * plan.price_per_unit
        assert self.account_repository.get_account_balance(self.buyer.account) == -costs
        assert (
            self.account_repository.get_account_balance(plan.planner.product_account)
            == costs
        )

    def test_that_correct_transaction_is_added_when_plan_is_public_service(self):
        plan = self.plan_generator.create_plan(
            is_public_service=True,
            activation_date=self.datetime_service.now_minus_one_day(),
        )
        pieces = 3
        self.pay_consumer_product(self.make_request(plan.id, pieces))
        assert len(self.transaction_repository.transactions) == 1
        transaction_added = self.transaction_repository.transactions[0]
        expected_amount = 0
        assert transaction_added.sending_account == self.buyer.account
        assert transaction_added.receiving_account == plan.planner.product_account
        assert transaction_added.amount == expected_amount

    def test_balances_are_adjusted_correctly_when_plan_is_public_service(self):
        plan = self.plan_generator.create_plan(
            is_public_service=True,
            activation_date=self.datetime_service.now_minus_one_day(),
        )
        pieces = 3
        self.pay_consumer_product(self.make_request(plan.id, pieces))
        costs = pieces * plan.price_per_unit
        assert self.account_repository.get_account_balance(self.buyer.account) == -costs
        assert (
            self.account_repository.get_account_balance(plan.planner.product_account)
            == costs
        )

    def test_correct_purchase_is_added(self):
        plan = self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_one_day()
        )
        pieces = 3
        self.pay_consumer_product(self.make_request(plan.id, pieces))
        assert len(self.purchase_repository.purchases) == 1
        purchase_added = self.purchase_repository.purchases[0]
        assert purchase_added.price_per_unit == plan.price_per_unit
        assert purchase_added.amount == pieces
        assert purchase_added.purpose == PurposesOfPurchases.consumption
        assert purchase_added.buyer == self.buyer
        assert purchase_added.plan == plan

    def test_correct_purchase_is_added_when_plan_is_public_service(self):
        plan = self.plan_generator.create_plan(
            is_public_service=True,
            activation_date=self.datetime_service.now_minus_one_day(),
        )
        pieces = 3
        self.pay_consumer_product(self.make_request(plan.id, pieces))
        assert len(self.purchase_repository.purchases) == 1
        purchase_added = self.purchase_repository.purchases[0]
        assert purchase_added.price_per_unit == 0
        assert purchase_added.plan == plan

    def test_payment_fails_when_plan_does_not_exist(self):
        response = self.pay_consumer_product(self.make_request(uuid4(), 1))
        self.assertFalse(response.is_accepted)
        self.assertEqual(response.rejection_reason, RejectionReason.plan_not_found)

    def make_request(
        self, plan: UUID, amount: int
    ) -> PayConsumerProductRequestTestImpl:
        return PayConsumerProductRequestTestImpl(
            buyer=self.buyer.id,
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
