from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from arbeitszeit.entities import ProductionCosts, PurposesOfPurchases
from arbeitszeit.use_cases import PayConsumerProduct
from arbeitszeit.use_cases.pay_consumer_product import RejectionReason
from arbeitszeit.use_cases.update_plans_and_payout import UpdatePlansAndPayout
from tests.control_thresholds import ControlThresholdsTestImpl
from tests.data_generators import TransactionGenerator

from .base_test_case import BaseTestCase
from .repositories import (
    AccountRepository,
    CompanyRepository,
    PlanCooperationRepository,
    PurchaseRepository,
    TransactionRepository,
)


class PayConsumerProductTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.transaction_generator = self.injector.get(TransactionGenerator)
        self.pay_consumer_product = self.injector.get(PayConsumerProduct)
        self.transaction_repository = self.injector.get(TransactionRepository)
        self.account_repository = self.injector.get(AccountRepository)
        self.purchase_repository = self.injector.get(PurchaseRepository)
        self.plan_cooperation_repository = self.injector.get(PlanCooperationRepository)
        self.buyer = self.member_generator.create_member_entity()
        self.control_thresholds = self.injector.get(ControlThresholdsTestImpl)
        self.update_plans_and_payout = self.injector.get(UpdatePlansAndPayout)
        self.company_repository = self.injector.get(CompanyRepository)

    def test_payment_fails_when_plan_does_not_exist(self):
        response = self.pay_consumer_product.pay_consumer_product(
            self.make_request(uuid4(), 1)
        )
        self.assertFalse(response.is_accepted)
        self.assertEqual(response.rejection_reason, RejectionReason.plan_not_found)

    def test_payment_fails_when_buyer_does_not_exist(self):
        plan = self.plan_generator.create_plan()
        response = self.pay_consumer_product.pay_consumer_product(
            self.make_request(plan.id, 1, buyer=uuid4())
        )
        self.assertFalse(response.is_accepted)
        self.assertEqual(
            response.rejection_reason, RejectionReason.buyer_does_not_exist
        )

    def test_payment_is_unsuccessful_if_plan_is_expired(self):
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        plan = self.plan_generator.create_plan(
            timeframe=1,
        )
        self.update_plans_and_payout()
        self.datetime_service.freeze_time(datetime(2001, 1, 1))
        self.update_plans_and_payout()
        response = self.pay_consumer_product.pay_consumer_product(
            self.make_request(plan.id, amount=3)
        )
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

        response = self.pay_consumer_product.pay_consumer_product(
            self.make_request(plan.id, 3)
        )
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

        transactions_before_payment = len(self.transaction_repository.transactions)
        account = self.buyer.account
        assert self.account_repository.get_account_balance(account) == 0
        self.control_thresholds.set_allowed_overdraw_of_member_account(0)

        self.pay_consumer_product.pay_consumer_product(
            self.make_request(plan.id, amount=3)
        )
        self.assertEqual(
            len(self.transaction_repository.transactions), transactions_before_payment
        )

    def test_no_purchase_is_added_when_member_has_insufficient_balance(
        self,
    ):
        plan = self.plan_generator.create_plan(
            activation_date=self.datetime_service.now(),
        )

        account = self.buyer.account
        assert self.account_repository.get_account_balance(account) == 0
        self.control_thresholds.set_allowed_overdraw_of_member_account(0)

        self.pay_consumer_product.pay_consumer_product(
            self.make_request(plan.id, amount=3)
        )
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

        response = self.pay_consumer_product.pay_consumer_product(
            self.make_request(plan.id, 3)
        )
        self.assertTrue(response.is_accepted)

    def test_payment_is_unsuccessful_if_member_without_certs_buys_value_of_10_and_has_account_limit_of_9(
        self,
    ):
        plan = self.plan_generator.create_plan(
            costs=ProductionCosts(
                means_cost=Decimal("4"),
                resource_cost=Decimal("4"),
                labour_cost=Decimal("2"),
            ),
            amount=1,
        )

        account = self.buyer.account
        assert self.account_repository.get_account_balance(account) == 0
        self.control_thresholds.set_allowed_overdraw_of_member_account(9)

        response = self.pay_consumer_product.pay_consumer_product(
            self.make_request(plan.id, amount=1)
        )
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

        response = self.pay_consumer_product.pay_consumer_product(
            self.make_request(plan.id, 1)
        )
        self.assertTrue(response.is_accepted)

    def test_that_correct_transaction_is_added(self):
        plan = self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_one_day()
        )
        transactions_before_payment = len(self.transaction_repository.transactions)
        pieces = 3
        self.make_transaction_to_buyer_account(Decimal(100))
        self.pay_consumer_product.pay_consumer_product(
            self.make_request(plan.id, pieces)
        )
        self.assertEqual(
            len(self.transaction_repository.transactions),
            transactions_before_payment + 2,
        )
        transaction_added = self.transaction_repository.transactions[-1]
        expected_amount_sent = pieces * self.price_checker.get_unit_price(plan.id)
        expected_amount_received = pieces * self.price_checker.get_unit_cost(plan.id)
        planner = self.company_repository.get_companies().with_id(plan.planner).first()
        assert transaction_added.sending_account == self.buyer.account
        assert transaction_added.receiving_account == planner.product_account
        assert transaction_added.amount_sent == expected_amount_sent
        assert transaction_added.amount_received == expected_amount_received

    def test_balances_are_adjusted_correctly(self) -> None:
        plan = self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_one_day(),
            costs=ProductionCosts(
                means_cost=Decimal(3),
                resource_cost=Decimal(3),
                labour_cost=Decimal(3),
            ),
            amount=4,
        )
        start_balance = Decimal(100)
        self.make_transaction_to_buyer_account(start_balance)
        bought_pieces = 2
        self.pay_consumer_product.pay_consumer_product(
            self.make_request(plan.id, bought_pieces)
        )
        costs = bought_pieces * self.price_checker.get_unit_price(plan.id)

        expected_balance = start_balance - costs
        self.assertEqual(
            self.account_repository.get_account_balance(self.buyer.account),
            expected_balance,
        )
        planner = self.company_repository.get_companies().with_id(plan.planner).first()
        assert planner
        self.assertEqual(
            self.account_repository.get_account_balance(planner.product_account),
            Decimal("-9") + costs,
        )

    def test_that_correct_transaction_is_added_when_plan_is_public_service(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan(
            is_public_service=True,
            activation_date=self.datetime_service.now_minus_one_day(),
        )
        transactions_before_payment = len(self.transaction_repository.transactions)
        pieces = 3
        self.pay_consumer_product.pay_consumer_product(
            self.make_request(plan.id, pieces)
        )
        self.assertEqual(
            len(self.transaction_repository.transactions),
            transactions_before_payment + 1,
        )
        transaction_added = self.transaction_repository.transactions[-1]
        planner = self.company_repository.get_companies().with_id(plan.planner).first()
        assert transaction_added.sending_account == self.buyer.account
        assert transaction_added.receiving_account == planner.product_account
        assert transaction_added.amount_sent == transaction_added.amount_received == 0

    def test_balances_are_adjusted_correctly_when_plan_is_public_service(self) -> None:
        plan = self.plan_generator.create_plan(
            is_public_service=True,
            activation_date=self.datetime_service.now_minus_one_day(),
        )
        pieces = 3
        self.pay_consumer_product.pay_consumer_product(
            self.make_request(plan.id, pieces)
        )
        costs = pieces * self.price_checker.get_unit_price(plan.id)
        planner = self.company_repository.get_companies().with_id(plan.planner).first()
        assert self.account_repository.get_account_balance(self.buyer.account) == -costs
        assert (
            self.account_repository.get_account_balance(planner.product_account)
            == costs
        )

    def test_correct_purchase_is_added(self):
        plan = self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_one_day()
        )
        self.make_transaction_to_buyer_account(Decimal("100"))
        pieces = 3
        self.pay_consumer_product.pay_consumer_product(
            self.make_request(plan.id, pieces)
        )
        assert len(self.purchase_repository.purchases) == 1
        purchase_added = self.purchase_repository.purchases[0]
        assert purchase_added.price_per_unit == self.price_checker.get_unit_price(
            plan.id
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
        self.pay_consumer_product.pay_consumer_product(
            self.make_request(plan.id, pieces)
        )
        assert len(self.purchase_repository.purchases) == 1
        purchase_added = self.purchase_repository.purchases[0]
        assert purchase_added.price_per_unit == 0
        assert purchase_added.plan == plan.id

    def make_request(
        self, plan: UUID, amount: int, buyer: Optional[UUID] = None
    ) -> PayConsumerProductRequestTestImpl:
        if buyer is None:
            buyer = self.buyer.id
        return PayConsumerProductRequestTestImpl(
            buyer=buyer,
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
