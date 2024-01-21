from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from arbeitszeit.records import ProductionCosts
from arbeitszeit.use_cases import query_private_consumptions
from arbeitszeit.use_cases.register_hours_worked import (
    RegisterHoursWorked,
    RegisterHoursWorkedRequest,
)
from arbeitszeit.use_cases.register_private_consumption import (
    RegisterPrivateConsumption,
    RegisterPrivateConsumptionRequest,
    RejectionReason,
)

from .base_test_case import BaseTestCase


class RegisterPrivateConsumptionTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.register_private_consumption = self.injector.get(
            RegisterPrivateConsumption
        )
        self.consumer = self.member_generator.create_member()
        self.query_private_consumptions = self.injector.get(
            query_private_consumptions.QueryPrivateConsumptions
        )
        self.register_hours_worked = self.injector.get(RegisterHoursWorked)

    def test_registration_fails_when_plan_does_not_exist(self) -> None:
        response = self.register_private_consumption.register_private_consumption(
            self.make_request(uuid4(), 1)
        )
        self.assertFalse(response.is_accepted)
        self.assertEqual(response.rejection_reason, RejectionReason.plan_not_found)

    def test_registration_fails_when_consumer_does_not_exist(self) -> None:
        plan = self.plan_generator.create_plan()
        response = self.register_private_consumption.register_private_consumption(
            self.make_request(plan, 1, consumer=uuid4())
        )
        self.assertFalse(response.is_accepted)
        self.assertEqual(
            response.rejection_reason, RejectionReason.consumer_does_not_exist
        )

    def test_registration_is_unsuccessful_if_plan_is_expired(self) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        plan = self.plan_generator.create_plan(
            timeframe=1,
        )
        self.datetime_service.freeze_time(datetime(2001, 1, 1))
        response = self.register_private_consumption.register_private_consumption(
            self.make_request(plan, amount=3)
        )
        self.assertFalse(response.is_accepted)
        self.assertEqual(response.rejection_reason, RejectionReason.plan_inactive)

    def test_registration_is_unsuccessful_if_member_has_no_certs_and_an_account_limit_of_zero(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        assert self.balance_checker.get_member_account_balance(self.consumer) == 0
        self.control_thresholds.set_allowed_overdraw_of_member_account(0)

        response = self.register_private_consumption.register_private_consumption(
            self.make_request(plan, 3)
        )
        self.assertFalse(response.is_accepted)
        self.assertEqual(
            response.rejection_reason, RejectionReason.insufficient_balance
        )

    def test_no_consumption_is_added_when_member_has_insufficient_balance(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        assert self.balance_checker.get_member_account_balance(self.consumer) == 0
        self.control_thresholds.set_allowed_overdraw_of_member_account(0)

        self.register_private_consumption.register_private_consumption(
            self.make_request(plan, amount=3)
        )
        response = self.query_private_consumptions.query_private_consumptions(
            query_private_consumptions.Request(member=self.consumer)
        )
        assert len(response.consumptions) == 0

    def test_registration_is_successful_if_member_has_negative_certs_and_consumes_public_product(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan(is_public_service=True)
        self.make_transaction_to_consumer_account(Decimal("-10"))
        assert self.balance_checker.get_member_account_balance(
            self.consumer
        ) == Decimal("-10")
        self.control_thresholds.set_allowed_overdraw_of_member_account(0)

        response = self.register_private_consumption.register_private_consumption(
            self.make_request(plan, 3)
        )
        self.assertTrue(response.is_accepted)

    def test_registration_is_unsuccessful_if_member_without_certs_consumes_value_of_10_and_has_account_limit_of_9(
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
        assert self.balance_checker.get_member_account_balance(self.consumer) == 0
        self.control_thresholds.set_allowed_overdraw_of_member_account(9)

        response = self.register_private_consumption.register_private_consumption(
            self.make_request(plan, amount=1)
        )
        self.assertFalse(response.is_accepted)
        self.assertEqual(
            response.rejection_reason, RejectionReason.insufficient_balance
        )

    def test_registration_is_successful_if_member_without_certs_consumes_value_of_10_and_has_account_limit_of_11(
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
        assert self.balance_checker.get_member_account_balance(self.consumer) == 0
        self.control_thresholds.set_allowed_overdraw_of_member_account(11)

        response = self.register_private_consumption.register_private_consumption(
            self.make_request(plan, 1)
        )
        self.assertTrue(response.is_accepted)

    def test_balances_are_adjusted_correctly(self) -> None:
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            costs=ProductionCosts(
                means_cost=Decimal(3),
                resource_cost=Decimal(3),
                labour_cost=Decimal(3),
            ),
            amount=4,
            planner=planner,
        )
        start_balance = Decimal(100)
        self.make_transaction_to_consumer_account(start_balance)
        pieces_consumed = 2
        self.register_private_consumption.register_private_consumption(
            self.make_request(plan, pieces_consumed)
        )
        costs = pieces_consumed * self.price_checker.get_unit_price(plan)
        expected_balance = start_balance - costs
        assert (
            self.balance_checker.get_member_account_balance(self.consumer)
            == expected_balance
        )
        assert (
            self.balance_checker.get_company_account_balances(planner).prd_account
            == Decimal("-9") + costs
        )

    def test_balances_are_adjusted_correctly_when_plan_is_public_service(self) -> None:
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(is_public_service=True, planner=planner)
        pieces = 3
        self.register_private_consumption.register_private_consumption(
            self.make_request(plan, pieces)
        )
        costs = pieces * self.price_checker.get_unit_price(plan)
        assert self.balance_checker.get_member_account_balance(self.consumer) == -costs
        assert (
            self.balance_checker.get_company_account_balances(planner).prd_account
            == costs
        )

    def test_correct_consumption_is_added(self) -> None:
        plan = self.plan_generator.create_plan()
        self.make_transaction_to_consumer_account(Decimal("100"))
        pieces = 3
        self.register_private_consumption.register_private_consumption(
            self.make_request(plan, pieces)
        )
        response = self.query_private_consumptions.query_private_consumptions(
            query_private_consumptions.Request(member=self.consumer)
        )
        assert len(response.consumptions) == 1
        latest_consumption = response.consumptions[0]
        assert latest_consumption.price_per_unit == self.price_checker.get_unit_price(
            plan
        )
        assert latest_consumption.amount == pieces
        assert latest_consumption.plan_id == plan

    def test_correct_consumption_is_added_when_plan_is_public_service(self) -> None:
        plan = self.plan_generator.create_plan(is_public_service=True)
        pieces = 3
        self.register_private_consumption.register_private_consumption(
            self.make_request(plan, pieces)
        )
        response = self.query_private_consumptions.query_private_consumptions(
            query_private_consumptions.Request(member=self.consumer)
        )
        assert len(response.consumptions) == 1
        latest_consumption = response.consumptions[0]
        assert latest_consumption.price_per_unit == Decimal(0)
        assert latest_consumption.plan_id == plan

    def make_request(
        self, plan: UUID, amount: int, consumer: Optional[UUID] = None
    ) -> RegisterPrivateConsumptionRequest:
        if consumer is None:
            consumer = self.consumer
        return RegisterPrivateConsumptionRequest(
            consumer=consumer,
            plan=plan,
            amount=amount,
        )

    def make_transaction_to_consumer_account(self, amount: Decimal) -> None:
        if amount > 0:
            company = self.company_generator.create_company(workers=[self.consumer])
            self.register_hours_worked(
                RegisterHoursWorkedRequest(
                    company_id=company,
                    worker_id=self.consumer,
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
            self.consumption_generator.create_private_consumption(
                consumer=self.consumer,
                plan=plan,
                amount=1,
            )
