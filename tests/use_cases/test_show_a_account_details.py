from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from arbeitszeit.records import ProductionCosts
from arbeitszeit.transactions import TransactionTypes
from arbeitszeit.use_cases.register_hours_worked import (
    RegisterHoursWorked,
    RegisterHoursWorkedRequest,
)
from arbeitszeit.use_cases.show_a_account_details import ShowAAccountDetailsUseCase
from tests.use_cases.base_test_case import BaseTestCase


class UseCaseTester(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.show_a_account_details = self.injector.get(ShowAAccountDetailsUseCase)
        self.register_hours_worked = self.injector.get(RegisterHoursWorked)

    def test_no_transactions_returned_when_no_transactions_took_place(self) -> None:
        self.member_generator.create_member()
        company = self.company_generator.create_company()
        response = self.show_a_account_details(company)
        assert not response.transactions

    def test_balance_is_zero_when_no_transactions_took_place(self) -> None:
        self.member_generator.create_member()
        company = self.company_generator.create_company()
        response = self.show_a_account_details(company)
        assert response.account_balance == 0

    def test_company_id_is_returned(self):
        self.member_generator.create_member()
        company = self.company_generator.create_company_record()
        response = self.show_a_account_details(company.id)
        assert response.company_id == company.id

    def test_that_no_info_is_generated_after_selling_of_consumer_product(self) -> None:
        company = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=company)
        response = self.show_a_account_details(company)
        transactions_before_purchase = len(response.transactions)
        self.purchase_generator.create_purchase_by_member(plan=plan.id)
        response = self.show_a_account_details(company)
        assert len(response.transactions) == transactions_before_purchase

    def test_that_no_info_is_generated_when_company_sells_p(self) -> None:
        company = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=company)
        response = self.show_a_account_details(company)
        transactions_before_purchase = len(response.transactions)
        self.purchase_generator.create_fixed_means_purchase(plan=plan.id)
        response = self.show_a_account_details(company)
        assert len(response.transactions) == transactions_before_purchase

    def test_after_approving_a_plan_one_transaction_is_recorded(self) -> None:
        company = self.company_generator.create_company()
        self.plan_generator.create_plan(planner=company)
        response = self.show_a_account_details(company)
        assert len(response.transactions) == 1

    def test_after_approving_a_plan_and_registering_work_two_transactions_are_recorded(
        self,
    ) -> None:
        member = self.member_generator.create_member()
        company = self.company_generator.create_company(workers=[member])
        self.plan_generator.create_plan(planner=company)
        self.register_hours_worked(
            RegisterHoursWorkedRequest(
                company_id=company,
                worker_id=member,
                hours_worked=Decimal(2),
            )
        )
        response = self.show_a_account_details(company)
        assert len(response.transactions) == 2

    def test_two_transactions_are_recorded_in_descending_order(self) -> None:
        member = self.member_generator.create_member()
        company = self.company_generator.create_company(workers=[member])
        self.plan_generator.create_plan(planner=company)
        self.register_hours_worked(
            RegisterHoursWorkedRequest(
                company_id=company,
                worker_id=member,
                hours_worked=Decimal(2),
            )
        )
        response = self.show_a_account_details(company)
        assert (
            response.transactions[0].transaction_type
            == TransactionTypes.payment_of_wages
        )
        assert (
            response.transactions[1].transaction_type
            == TransactionTypes.credit_for_wages
        )

    def test_that_correct_info_is_generated_when_credit_for_wages_is_granted(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        self.plan_generator.create_plan(
            planner=company,
            costs=ProductionCosts(
                labour_cost=Decimal(8.5),
                means_cost=Decimal(0),
                resource_cost=Decimal(0),
            ),
        )
        response = self.show_a_account_details(company)
        assert len(response.transactions) == 1
        assert response.transactions[0].transaction_volume == Decimal(8.5)
        assert response.transactions[0].purpose is not None
        assert isinstance(response.transactions[0].date, datetime)
        assert (
            response.transactions[0].transaction_type
            == TransactionTypes.credit_for_wages
        )
        assert response.account_balance == Decimal(8.5)

    def test_that_correct_info_is_generated_after_company_transfering_work_certificates(
        self,
    ) -> None:
        hours_worked = Decimal("8.5")
        member = self.member_generator.create_member()
        company = self.company_generator.create_company(workers=[member])
        self.register_hours_worked(
            RegisterHoursWorkedRequest(
                company_id=company,
                worker_id=member,
                hours_worked=hours_worked,
            )
        )
        response = self.show_a_account_details(company)
        transaction = response.transactions[0]
        assert transaction.transaction_type == TransactionTypes.payment_of_wages
        assert transaction.transaction_volume == -hours_worked
        assert response.account_balance == -hours_worked

    def test_that_plotting_info_is_empty_when_no_transactions_occurred(self) -> None:
        self.member_generator.create_member()
        company = self.company_generator.create_company_record()
        response = self.show_a_account_details(company.id)
        assert not response.plot.timestamps
        assert not response.plot.accumulated_volumes

    def test_that_plotting_info_is_generated_after_transfer_of_work_certificates(
        self,
    ) -> None:
        hours_worked = Decimal("8.5")
        worker = self.member_generator.create_member()
        own_company = self.company_generator.create_company(workers=[worker])
        self.register_hours_worked(
            RegisterHoursWorkedRequest(
                company_id=own_company,
                worker_id=worker,
                hours_worked=hours_worked,
            )
        )
        response = self.show_a_account_details(own_company)
        assert response.plot.timestamps
        assert response.plot.accumulated_volumes

    def test_that_correct_plotting_info_is_generated_after_transferring_of_work_certs_to_two_workers(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        worker1 = self.member_generator.create_member()
        worker2 = self.member_generator.create_member()
        own_company = self.company_generator.create_company(workers=[worker1, worker2])
        expected_transaction_1_timestamp = datetime(2000, 1, 2)
        self.datetime_service.freeze_time(expected_transaction_1_timestamp)
        self.register_hours_worked(
            RegisterHoursWorkedRequest(
                company_id=own_company,
                worker_id=worker1,
                hours_worked=Decimal("10"),
            )
        )
        expected_transaction_2_timestamp = datetime(2000, 1, 3)
        self.datetime_service.freeze_time(expected_transaction_2_timestamp)
        self.register_hours_worked(
            RegisterHoursWorkedRequest(
                company_id=own_company,
                worker_id=worker2,
                hours_worked=Decimal("10"),
            )
        )
        response = self.show_a_account_details(own_company)
        assert len(response.plot.timestamps) == 2
        assert len(response.plot.accumulated_volumes) == 2

        assert expected_transaction_1_timestamp in response.plot.timestamps
        assert expected_transaction_2_timestamp in response.plot.timestamps

        assert Decimal("-10") in response.plot.accumulated_volumes
        assert Decimal("-20") in response.plot.accumulated_volumes

    def test_that_plotting_info_is_generated_in_the_correct_order_after_transfer_of_certs_to_three_workers(
        self,
    ) -> None:
        worker1 = self.member_generator.create_member()
        worker2 = self.member_generator.create_member()
        worker3 = self.member_generator.create_member()
        own_company = self.company_generator.create_company_record(
            workers=[worker1, worker2, worker3]
        )

        first_transaction_timestamp = datetime(2000, 1, 1)
        self.datetime_service.freeze_time(first_transaction_timestamp)
        self.register_hours_worked(
            RegisterHoursWorkedRequest(
                company_id=own_company.id,
                worker_id=worker1,
                hours_worked=Decimal("10"),
            )
        )
        seconds_transaction_timestamp = datetime(2000, 1, 2)
        self.datetime_service.freeze_time(seconds_transaction_timestamp)
        self.register_hours_worked(
            RegisterHoursWorkedRequest(
                company_id=own_company.id,
                worker_id=worker2,
                hours_worked=Decimal("10"),
            )
        )
        third_transaction_timestamp = datetime(2000, 1, 3)
        self.datetime_service.freeze_time(third_transaction_timestamp)
        self.register_hours_worked(
            RegisterHoursWorkedRequest(
                company_id=own_company.id,
                worker_id=worker3,
                hours_worked=Decimal("10"),
            )
        )

        response = self.show_a_account_details(own_company.id)
        assert response.plot.timestamps[0] == first_transaction_timestamp
        assert response.plot.timestamps[2] == third_transaction_timestamp

        assert response.plot.accumulated_volumes[0] == Decimal(-10)
        assert response.plot.accumulated_volumes[2] == Decimal(-30)

    def test_that_correct_plotting_info_is_generated_after_receiving_of_work_certificates_from_social_accounting(
        self,
    ) -> None:
        transaction_timestamp = datetime(2030, 1, 1)
        expected_labour_time = Decimal(123)
        self.datetime_service.freeze_time(transaction_timestamp)
        company = self.company_generator.create_company()
        self.plan_generator.create_plan(
            planner=company,
            costs=ProductionCosts(
                labour_cost=expected_labour_time,
                means_cost=Decimal(0),
                resource_cost=Decimal(0),
            ),
        )
        response = self.show_a_account_details(company)

        assert response.plot.timestamps
        assert response.plot.accumulated_volumes

        assert len(response.plot.timestamps) == 1
        assert len(response.plot.accumulated_volumes) == 1

        assert transaction_timestamp in response.plot.timestamps
        assert expected_labour_time in response.plot.accumulated_volumes
