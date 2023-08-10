from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from arbeitszeit.entities import ProductionCosts
from arbeitszeit.use_cases import query_member_purchases
from arbeitszeit.use_cases.pay_consumer_product import (
    PayConsumerProduct,
    PayConsumerProductRequest,
    RejectionReason,
)
from arbeitszeit.use_cases.register_hours_worked import (
    RegisterHoursWorked,
    RegisterHoursWorkedRequest,
)

from .base_test_case import BaseTestCase
from .repositories import EntityStorage


class PayConsumerProductTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.pay_consumer_product = self.injector.get(PayConsumerProduct)
        self.entity_storage = self.injector.get(EntityStorage)
        self.buyer = self.member_generator.create_member()
        self.query_member_purchases = self.injector.get(
            query_member_purchases.QueryMemberPurchases
        )
        self.register_hours_worked = self.injector.get(RegisterHoursWorked)

    def test_payment_fails_when_plan_does_not_exist(self) -> None:
        response = self.pay_consumer_product.pay_consumer_product(
            self.make_request(uuid4(), 1)
        )
        self.assertFalse(response.is_accepted)
        self.assertEqual(response.rejection_reason, RejectionReason.plan_not_found)

    def test_payment_fails_when_buyer_does_not_exist(self) -> None:
        plan = self.plan_generator.create_plan()
        response = self.pay_consumer_product.pay_consumer_product(
            self.make_request(plan.id, 1, buyer=uuid4())
        )
        self.assertFalse(response.is_accepted)
        self.assertEqual(
            response.rejection_reason, RejectionReason.buyer_does_not_exist
        )

    def test_payment_is_unsuccessful_if_plan_is_expired(self) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        plan = self.plan_generator.create_plan(
            timeframe=1,
        )
        self.datetime_service.freeze_time(datetime(2001, 1, 1))
        response = self.pay_consumer_product.pay_consumer_product(
            self.make_request(plan.id, amount=3)
        )
        self.assertFalse(response.is_accepted)
        self.assertEqual(response.rejection_reason, RejectionReason.plan_inactive)

    def test_payment_is_unsuccessful_if_member_has_no_certs_and_an_account_limit_of_zero(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        assert self.balance_checker.get_member_account_balance(self.buyer) == 0
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
    ) -> None:
        plan = self.plan_generator.create_plan()

        transactions_before_payment = len(self.entity_storage.get_transactions())
        assert self.balance_checker.get_member_account_balance(self.buyer) == 0
        self.control_thresholds.set_allowed_overdraw_of_member_account(0)

        self.pay_consumer_product.pay_consumer_product(
            self.make_request(plan.id, amount=3)
        )
        self.assertEqual(
            len(self.entity_storage.get_transactions()),
            transactions_before_payment,
        )

    def test_no_purchase_is_added_when_member_has_insufficient_balance(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        assert self.balance_checker.get_member_account_balance(self.buyer) == 0
        self.control_thresholds.set_allowed_overdraw_of_member_account(0)

        self.pay_consumer_product.pay_consumer_product(
            self.make_request(plan.id, amount=3)
        )
        user_purchases = list(self.query_member_purchases(self.buyer))
        assert len(user_purchases) == 0

    def test_payment_is_successful_if_member_has_negative_certs_and_buys_public_product(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan(is_public_service=True)
        self.make_transaction_to_buyer_account(Decimal("-10"))
        assert self.balance_checker.get_member_account_balance(self.buyer) == Decimal(
            "-10"
        )
        self.control_thresholds.set_allowed_overdraw_of_member_account(0)

        response = self.pay_consumer_product.pay_consumer_product(
            self.make_request(plan.id, 3)
        )
        self.assertTrue(response.is_accepted)

    def test_payment_is_unsuccessful_if_member_without_certs_buys_value_of_10_and_has_account_limit_of_9(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan(
            costs=ProductionCosts(
                means_cost=Decimal("4"),
                resource_cost=Decimal("4"),
                labour_cost=Decimal("2"),
            ),
            amount=1,
        )
        assert self.balance_checker.get_member_account_balance(self.buyer) == 0
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
    ) -> None:
        plan = self.plan_generator.create_plan(
            costs=ProductionCosts(
                means_cost=Decimal("4"),
                resource_cost=Decimal("4"),
                labour_cost=Decimal("2"),
            ),
            amount=1,
            cooperation=None,
        )
        assert self.balance_checker.get_member_account_balance(self.buyer) == 0
        self.control_thresholds.set_allowed_overdraw_of_member_account(11)

        response = self.pay_consumer_product.pay_consumer_product(
            self.make_request(plan.id, 1)
        )
        self.assertTrue(response.is_accepted)

    def test_balances_are_adjusted_correctly(self) -> None:
        plan = self.plan_generator.create_plan(
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
        assert (
            self.balance_checker.get_member_account_balance(self.buyer)
            == expected_balance
        )
        planner = self.entity_storage.get_companies().with_id(plan.planner).first()
        assert planner
        assert (
            self.balance_checker.get_company_account_balances(planner.id).prd_account
            == Decimal("-9") + costs
        )

    def test_balances_are_adjusted_correctly_when_plan_is_public_service(self) -> None:
        plan = self.plan_generator.create_plan(is_public_service=True)
        pieces = 3
        self.pay_consumer_product.pay_consumer_product(
            self.make_request(plan.id, pieces)
        )
        costs = pieces * self.price_checker.get_unit_price(plan.id)
        planner = self.entity_storage.get_companies().with_id(plan.planner).first()
        assert planner
        assert self.balance_checker.get_member_account_balance(self.buyer) == -costs
        assert (
            self.balance_checker.get_company_account_balances(planner.id).prd_account
            == costs
        )

    def test_correct_purchase_is_added(self) -> None:
        plan = self.plan_generator.create_plan()
        self.make_transaction_to_buyer_account(Decimal("100"))
        pieces = 3
        self.pay_consumer_product.pay_consumer_product(
            self.make_request(plan.id, pieces)
        )
        user_purchases = list(self.query_member_purchases(self.buyer))
        assert len(user_purchases) == 1
        latest_purchase = user_purchases[0]
        assert latest_purchase.price_per_unit == self.price_checker.get_unit_price(
            plan.id
        )
        assert latest_purchase.amount == pieces
        assert latest_purchase.plan_id == plan.id

    def test_correct_purchase_is_added_when_plan_is_public_service(self) -> None:
        plan = self.plan_generator.create_plan(is_public_service=True)
        pieces = 3
        self.pay_consumer_product.pay_consumer_product(
            self.make_request(plan.id, pieces)
        )
        user_purchases = list(self.query_member_purchases(self.buyer))
        assert len(user_purchases) == 1
        latest_purchase = user_purchases[0]
        assert latest_purchase.price_per_unit == Decimal(0)
        assert latest_purchase.plan_id == plan.id

    def make_request(
        self, plan: UUID, amount: int, buyer: Optional[UUID] = None
    ) -> PayConsumerProductRequest:
        if buyer is None:
            buyer = self.buyer
        return PayConsumerProductRequest(
            buyer=buyer,
            plan=plan,
            amount=amount,
        )

    def make_transaction_to_buyer_account(self, amount: Decimal) -> None:
        if amount > 0:
            company = self.company_generator.create_company(workers=[self.buyer])
            self.register_hours_worked(
                RegisterHoursWorkedRequest(
                    company_id=company,
                    worker_id=self.buyer,
                    hours_worked=amount,
                )
            )
        else:
            amount = -amount
            plan = self.plan_generator.create_plan(
                amount=1,
                costs=ProductionCosts(
                    labour_cost=amount,
                    means_cost=Decimal(0),
                    resource_cost=Decimal(0),
                ),
            )
            self.purchase_generator.create_purchase_by_member(
                buyer=self.buyer,
                plan=plan.id,
                amount=1,
            )
