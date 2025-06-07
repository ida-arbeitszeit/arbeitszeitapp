from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from parameterized import parameterized

from arbeitszeit.records import PrivateConsumption, ProductionCosts, Transfer
from arbeitszeit.repositories import DatabaseGateway
from arbeitszeit.transfers.transfer_type import TransferType
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


class RegisterPrivateConsumptionBase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.register_private_consumption = self.injector.get(
            RegisterPrivateConsumption
        )
        self.database_gateway = self.injector.get(DatabaseGateway)

    def create_cooperating_plans_with(
        self, *, costs_per_unit: list[Decimal]
    ) -> list[UUID]:
        plans = [self.create_plan_with(cost_per_unit=cost) for cost in costs_per_unit]
        self.cooperation_generator.create_cooperation(
            plans=plans,
        )
        return plans

    def create_plan_with(self, *, cost_per_unit: Decimal) -> UUID:
        plan = self.plan_generator.create_plan(
            costs=ProductionCosts(
                labour_cost=cost_per_unit,
                means_cost=Decimal(0),
                resource_cost=Decimal(0),
            ),
            amount=1,
        )
        return plan

    def get_private_consumption_transfers(self) -> list[Transfer]:
        transfers = self.database_gateway.get_transfers()
        return list(
            filter(
                lambda t: t.type == TransferType.private_consumption,
                transfers,
            )
        )

    def get_compensation_transfers(self) -> list[Transfer]:
        transfers = self.database_gateway.get_transfers()
        return list(
            filter(
                lambda t: t.type == TransferType.compensation_for_coop
                or t.type == TransferType.compensation_for_company,
                transfers,
            )
        )


class RegisterPrivateConsumptionTests(RegisterPrivateConsumptionBase):
    def setUp(self) -> None:
        super().setUp()
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

    @parameterized.expand(
        [
            (Decimal("2"), 2),
            (Decimal("2"), 3),
            (Decimal("2"), None),
        ]
    )
    def test_registration_is_successful_if_member_without_certs_has_account_limit_that_equals_or_exceeds_the_product_price(
        self,
        price: Decimal,
        allowed_overdraw: int | None,
    ) -> None:
        plan = self.plan_generator.create_plan(
            costs=ProductionCosts(
                means_cost=Decimal(price),
                resource_cost=Decimal(0),
                labour_cost=Decimal(0),
            ),
            amount=1,
            cooperation=None,
        )
        assert self.balance_checker.get_member_account_balance(self.consumer) == 0
        self.control_thresholds.set_allowed_overdraw_of_member_account(allowed_overdraw)

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


class ConsumptionTransferTests(RegisterPrivateConsumptionBase):
    def test_that_no_private_consumption_transfer_is_created_if_consumer_balance_is_not_sufficient(
        self,
    ) -> None:
        consumer = self.member_generator.create_member()
        plan = self.plan_generator.create_plan()
        assert self.balance_checker.get_member_account_balance(consumer) == 0
        self.control_thresholds.set_allowed_overdraw_of_member_account(0)
        with self.assertRaises(RejectionReason):
            self.consumption_generator.create_private_consumption(
                consumer=consumer,
                plan=plan,
            )
        assert not self.get_private_consumption_transfers()

    @parameterized.expand(
        [
            (0,),
            (1,),
            (3,),
        ]
    )
    def test_that_one_private_consumption_transfer_is_created_for_each_consumption(
        self,
        number_of_consumptions: int,
    ) -> None:
        for _ in range(number_of_consumptions):
            self.consumption_generator.create_private_consumption()
        transfers = self.get_private_consumption_transfers()
        assert len(transfers) == number_of_consumptions

    def test_that_consumption_transfer_has_date_of_consumption(self) -> None:
        EXPECTED_DATE = datetime(2023, 10, 1, 12, 0, 0)
        self.datetime_service.freeze_time(EXPECTED_DATE)
        self.consumption_generator.create_private_consumption()
        transfers = self.get_private_consumption_transfers()
        assert len(transfers) == 1
        assert transfers[0].date == EXPECTED_DATE

    def test_that_debit_account_of_consumption_transfer_is_consumer_account(
        self,
    ) -> None:
        consumer = self.member_generator.create_member()
        self.consumption_generator.create_private_consumption(consumer=consumer)
        transfers = self.get_private_consumption_transfers()
        assert len(transfers) == 1
        assert transfers[0].debit_account == self.get_account_of(member=consumer)

    def test_that_credit_account_of_consumption_transfer_is_planner_product_account(
        self,
    ) -> None:
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=planner)
        self.consumption_generator.create_private_consumption(plan=plan)
        transfers = self.get_private_consumption_transfers()
        assert len(transfers) == 1
        assert transfers[0].credit_account == self.get_product_account_of(
            company=planner
        )

    @parameterized.expand(
        [
            (1, Decimal(3.1)),
            (2, Decimal(5)),
            (3, Decimal(10.6)),
        ]
    )
    def test_that_value_of_consumption_transfer_is_amount_times_price_per_unit(
        self,
        amount: int,
        price_per_unit: Decimal,
    ) -> None:
        plan = self.create_plan_with(
            cost_per_unit=price_per_unit,
        )
        self.consumption_generator.create_private_consumption(
            plan=plan,
            amount=amount,
        )
        transfers = self.get_private_consumption_transfers()
        assert len(transfers) == 1
        assert transfers[0].value == amount * price_per_unit

    def test_that_value_of_consumption_transfer_is_amount_times_coop_price_per_unit(
        self,
    ) -> None:
        AMOUNT = 4
        cooperating_plans = self.create_cooperating_plans_with(
            costs_per_unit=[Decimal(5), Decimal(10), Decimal(15)]
        )  # -> coop price per unit = 10
        self.consumption_generator.create_private_consumption(
            plan=cooperating_plans[
                0
            ],  # first plan has individual price of 5 and coop price of 10
            amount=AMOUNT,
        )
        transfers = self.get_private_consumption_transfers()
        assert len(transfers) == 1
        assert transfers[0].value == AMOUNT * Decimal(10)

    def get_account_of(self, *, member: UUID) -> UUID:
        account = self.database_gateway.get_accounts().owned_by_member(member).first()
        assert account
        return account.id

    def get_product_account_of(self, *, company: UUID) -> UUID:
        company_record = self.database_gateway.get_companies().with_id(company).first()
        assert company_record
        return company_record.product_account


class CompensationTransferTests(RegisterPrivateConsumptionBase):
    def test_no_compensation_transfer_created_after_consumption_of_cooperative_product_without_productivity_differences(
        self,
    ) -> None:
        COSTS_PER_UNIT = Decimal(3)
        cooperating_plans = self.create_cooperating_plans_with(
            costs_per_unit=[COSTS_PER_UNIT, COSTS_PER_UNIT]
        )
        self.consumption_generator.create_private_consumption(
            plan=cooperating_plans[0],
        )
        transfers = self.get_compensation_transfers()
        assert not transfers

    def test_no_compensation_transfer_created_when_consumed_plan_has_average_productivity(
        self,
    ) -> None:
        cooperating_plans = self.create_cooperating_plans_with(
            costs_per_unit=[Decimal(5), Decimal(10), Decimal(15)]
        )
        self.consumption_generator.create_private_consumption(
            plan=cooperating_plans[1],  # second plan has average productivity
        )
        transfers = self.get_compensation_transfers()
        assert not transfers

    @parameterized.expand(
        [
            (0,),
            (1,),
            (3,),
        ]
    )
    def test_one_compensation_transfer_created_for_each_consumption_of_cooperative_product_with_productivity_differences(
        self,
        number_of_consumptions: int,
    ) -> None:
        cooperating_plans = self.create_cooperating_plans_with(
            costs_per_unit=[Decimal(3), Decimal(10)]
        )
        for _ in range(number_of_consumptions):
            self.consumption_generator.create_private_consumption(
                plan=cooperating_plans[0],
            )
        transfers = self.get_compensation_transfers()
        assert len(transfers) == number_of_consumptions

    def test_that_compensation_for_cooperation_transfer_created_if_overproductive_plan_is_consumed(
        self,
    ) -> None:
        cooperating_plans = self.create_cooperating_plans_with(
            costs_per_unit=[Decimal(3), Decimal(10)]
        )
        self.consumption_generator.create_private_consumption(
            plan=cooperating_plans[0],  # first plan is overproductive
        )
        transfers = self.get_compensation_transfers()
        assert len(transfers) == 1
        assert transfers[0].type == TransferType.compensation_for_coop

    def test_that_compensation_for_company_created_if_underproductive_plan_is_consumed(
        self,
    ) -> None:
        cooperating_plans = self.create_cooperating_plans_with(
            costs_per_unit=[Decimal(3), Decimal(10)]
        )
        self.consumption_generator.create_private_consumption(
            plan=cooperating_plans[1],  # second plan is underproductive
        )
        transfers = self.get_compensation_transfers()
        assert len(transfers) == 1
        assert transfers[0].type == TransferType.compensation_for_company


class PrivateConsumptionRecordTests(RegisterPrivateConsumptionBase):
    @parameterized.expand(
        [
            (0,),
            (1,),
            (3,),
        ]
    )
    def test_that_for_each_private_consumption_one_record_is_created(
        self,
        number_of_consumptions: int,
    ) -> None:
        for _ in range(number_of_consumptions):
            self.consumption_generator.create_private_consumption()
        records = self.get_private_consumption_records()
        assert len(records) == number_of_consumptions

    def test_that_private_consumption_record_has_requested_amount(self) -> None:
        AMOUNT = 3
        self.consumption_generator.create_private_consumption(amount=AMOUNT)
        records = self.get_private_consumption_records()
        assert len(records) == 1
        assert records[0].amount == AMOUNT

    def test_that_private_consumption_record_has_consumed_plan_id(self) -> None:
        plan = self.plan_generator.create_plan()
        self.consumption_generator.create_private_consumption(plan=plan)
        records = self.get_private_consumption_records()
        assert len(records) == 1
        assert records[0].plan_id == plan

    def test_that_private_consumption_record_references_consumption_transfer_id(
        self,
    ) -> None:
        self.consumption_generator.create_private_consumption()
        transfers = self.get_private_consumption_transfers()
        assert len(transfers) == 1
        records = self.get_private_consumption_records()
        assert len(records) == 1
        assert records[0].transfer_of_private_consumption == transfers[0].id

    @parameterized.expand(
        [
            (False,),
            (True,),
        ]
    )
    def test_that_private_consumption_record_only_references_a_compensation_transfer_if_cooperation_has_productivity_differences(
        self,
        has_productivity_differences: bool = True,
    ) -> None:
        costs_per_unit = (
            [Decimal(3), Decimal(5)]
            if has_productivity_differences
            else [Decimal(3), Decimal(3)]
        )
        cooperating_plans = self.create_cooperating_plans_with(
            costs_per_unit=costs_per_unit
        )
        self.consumption_generator.create_private_consumption(
            plan=cooperating_plans[0],
        )
        compensation_transfers = self.get_compensation_transfers()
        records = self.get_private_consumption_records()
        assert len(records) == 1
        if has_productivity_differences:
            assert len(compensation_transfers) == 1
            assert records[0].transfer_of_compensation == compensation_transfers[0].id
        else:
            assert len(compensation_transfers) == 0
            assert records[0].transfer_of_compensation is None

    def get_private_consumption_records(self) -> list[PrivateConsumption]:
        records = self.database_gateway.get_private_consumptions()
        return list(records)
