from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from unittest import TestCase
from uuid import UUID, uuid4

from arbeitszeit.entities import ProductionCosts, PurposesOfPurchases
from arbeitszeit.price_calculator import calculate_price
from arbeitszeit.use_cases import PayConsumerProduct
from arbeitszeit.use_cases.pay_consumer_product import RejectionReason
from tests.control_thresholds import ControlThresholdsTestImpl
from tests.data_generators import MemberGenerator, PlanGenerator, TransactionGenerator
from tests.datetime_service import FakeDatetimeService

from .dependency_injection import get_dependency_injector
from .repositories import (
    AccountRepository,
    PlanCooperationRepository,
    PurchaseRepository,
    TransactionRepository,
)


class PayConsumerProductTests(TestCase):
    def setUp(self):
        injector = get_dependency_injector()
        self.member_generator = injector.get(MemberGenerator)
        self.plan_generator = injector.get(PlanGenerator)
        self.transaction_generator = injector.get(TransactionGenerator)
        self.pay_consumer_product = injector.get(PayConsumerProduct)
        self.datetime_service = injector.get(FakeDatetimeService)
        self.transaction_repository = injector.get(TransactionRepository)
        self.account_repository = injector.get(AccountRepository)
        self.purchase_repository = injector.get(PurchaseRepository)
        self.plan_cooperation_repository = injector.get(PlanCooperationRepository)
        self.buyer = self.member_generator.create_member()
        self.control_thresholds = injector.get(ControlThresholdsTestImpl)

    def test_payment_fails_when_plan_does_not_exist(self):
        response = self.pay_consumer_product(self.make_request(uuid4(), 1))
        self.assertFalse(response.is_accepted)
        self.assertEqual(response.rejection_reason, RejectionReason.plan_not_found)

    def test_payment_fails_if_plan_isnt_active_yet(self):
        plan = self.plan_generator.create_plan()
        response = self.pay_consumer_product(self.make_request(plan.id, amount=3))
        self.assertFalse(response.is_accepted)
        self.assertEqual(response.rejection_reason, RejectionReason.plan_inactive)

    def test_payment_is_unsuccessful_if_plan_is_expired(self):
        plan = self.plan_generator.create_plan(
            plan_creation_date=self.datetime_service.now_minus_ten_days(),
            timeframe=1,
        )
        plan.expired = True
        response = self.pay_consumer_product(self.make_request(plan.id, amount=3))
        self.assertFalse(response.is_accepted)
        self.assertEqual(response.rejection_reason, RejectionReason.plan_inactive)

    def test_payment_is_unsuccessful_if_member_has_no_certs_and_an_account_limit_of_zero(
        self,
    ):
        plan = self.plan_generator.create_plan(
            activation_date=self.datetime_service.now(),
        )
        account = self.buyer.account
        assert self.account_repository.get_account_balance(account) == 0
        self.control_thresholds.set_allowed_overdraw_of_member_account(0)

        response = self.pay_consumer_product(self.make_request(plan.id, 3))
        self.assertFalse(response.is_accepted)
        self.assertEqual(
            response.rejection_reason, RejectionReason.insufficient_balance
        )

    def test_no_transaction_is_added_when_member_has_insufficient_balance(
        self,
    ):
        plan = self.plan_generator.create_plan(
            activation_date=self.datetime_service.now(),
        )

        account = self.buyer.account
        assert self.account_repository.get_account_balance(account) == 0
        self.control_thresholds.set_allowed_overdraw_of_member_account(0)

        self.pay_consumer_product(self.make_request(plan.id, amount=3))
        assert len(self.transaction_repository.transactions) == 0

    def test_no_purchase_is_added_when_member_has_insufficient_balance(
        self,
    ):
        plan = self.plan_generator.create_plan(
            activation_date=self.datetime_service.now(),
        )

        account = self.buyer.account
        assert self.account_repository.get_account_balance(account) == 0
        self.control_thresholds.set_allowed_overdraw_of_member_account(0)

        self.pay_consumer_product(self.make_request(plan.id, amount=3))
        assert len(self.purchase_repository.purchases) == 0

    def test_payment_is_successful_if_member_has_negative_certs_and_buys_public_product(
        self,
    ):
        plan = self.plan_generator.create_plan(
            activation_date=self.datetime_service.now(), is_public_service=True
        )
        account = self.buyer.account
        self.make_transaction_to_buyer_account(Decimal("-10"))
        assert self.account_repository.get_account_balance(account) == Decimal("-10")
        self.control_thresholds.set_allowed_overdraw_of_member_account(0)

        response = self.pay_consumer_product(self.make_request(plan.id, 3))
        self.assertTrue(response.is_accepted)

    def test_payment_is_unsuccessful_if_member_without_certs_buys_value_of_10_and_has_account_limit_of_9(
        self,
    ):
        plan = self.plan_generator.create_plan(
            activation_date=self.datetime_service.now(),
            costs=ProductionCosts(
                means_cost=Decimal("4"),
                resource_cost=Decimal("4"),
                labour_cost=Decimal("2"),
            ),
            amount=1,
            cooperation=None,
        )

        account = self.buyer.account
        assert self.account_repository.get_account_balance(account) == 0
        self.control_thresholds.set_allowed_overdraw_of_member_account(9)

        response = self.pay_consumer_product(self.make_request(plan.id, amount=1))
        self.assertFalse(response.is_accepted)
        self.assertEqual(
            response.rejection_reason, RejectionReason.insufficient_balance
        )

    def test_payment_is_successful_if_member_without_certs_buys_value_of_10_and_has_account_limit_of_11(
        self,
    ):
        plan = self.plan_generator.create_plan(
            activation_date=self.datetime_service.now(),
            costs=ProductionCosts(
                means_cost=Decimal("4"),
                resource_cost=Decimal("4"),
                labour_cost=Decimal("2"),
            ),
            amount=1,
            cooperation=None,
        )
        account = self.buyer.account
        assert self.account_repository.get_account_balance(account) == 0
        self.control_thresholds.set_allowed_overdraw_of_member_account(11)

        response = self.pay_consumer_product(self.make_request(plan.id, 1))
        self.assertTrue(response.is_accepted)

    def test_that_correct_transaction_is_added(self):
        plan = self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_one_day()
        )
        pieces = 3
        self.make_transaction_to_buyer_account(Decimal(100))
        self.pay_consumer_product(self.make_request(plan.id, pieces))
        assert len(self.transaction_repository.transactions) == 2
        transaction_added = self.transaction_repository.transactions[1]
        expected_amount_sent = pieces * calculate_price(
            self.plan_cooperation_repository.get_cooperating_plans(plan.id)
        )
        expected_amount_received = pieces * calculate_price([plan])
        assert transaction_added.sending_account == self.buyer.account
        assert transaction_added.receiving_account == plan.planner.product_account
        assert transaction_added.amount_sent == expected_amount_sent
        assert transaction_added.amount_received == expected_amount_received

    def test_balances_are_adjusted_correctly(self) -> None:
        plan = self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_one_day()
        )
        start_balance = Decimal(100)
        self.make_transaction_to_buyer_account(start_balance)
        bought_pieces = 2
        self.pay_consumer_product(self.make_request(plan.id, bought_pieces))
        costs = bought_pieces * calculate_price(
            self.plan_cooperation_repository.get_cooperating_plans(plan.id)
        )

        expected_balance = start_balance - costs
        assert (
            self.account_repository.get_account_balance(self.buyer.account)
            == expected_balance
        )
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
        assert transaction_added.sending_account == self.buyer.account
        assert transaction_added.receiving_account == plan.planner.product_account
        assert transaction_added.amount_sent == transaction_added.amount_received == 0

    def test_balances_are_adjusted_correctly_when_plan_is_public_service(self):
        plan = self.plan_generator.create_plan(
            is_public_service=True,
            activation_date=self.datetime_service.now_minus_one_day(),
        )
        pieces = 3
        self.pay_consumer_product(self.make_request(plan.id, pieces))
        costs = pieces * calculate_price(
            self.plan_cooperation_repository.get_cooperating_plans(plan.id)
        )
        assert self.account_repository.get_account_balance(self.buyer.account) == -costs
        assert (
            self.account_repository.get_account_balance(plan.planner.product_account)
            == costs
        )

    def test_correct_purchase_is_added(self):
        plan = self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_one_day()
        )
        self.make_transaction_to_buyer_account(Decimal("100"))
        pieces = 3
        self.pay_consumer_product(self.make_request(plan.id, pieces))
        assert len(self.purchase_repository.purchases) == 1
        purchase_added = self.purchase_repository.purchases[0]
        assert purchase_added.price_per_unit == calculate_price(
            self.plan_cooperation_repository.get_cooperating_plans(plan.id)
        )
        assert purchase_added.amount == pieces
        assert purchase_added.purpose == PurposesOfPurchases.consumption
        assert purchase_added.buyer == self.buyer.id
        assert purchase_added.plan == plan.id

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
        assert purchase_added.plan == plan.id

    def make_request(
        self,
        plan: UUID,
        amount: int,
    ) -> PayConsumerProductRequestTestImpl:
        return PayConsumerProductRequestTestImpl(
            buyer=self.buyer.id,
            plan=plan,
            amount=amount,
        )

    def make_transaction_to_buyer_account(self, amount: Decimal) -> None:
        self.transaction_generator.create_transaction(
            receiving_account=self.buyer.account,
            amount_received=amount,
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
