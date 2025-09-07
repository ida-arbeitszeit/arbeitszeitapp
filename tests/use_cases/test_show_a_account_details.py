from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from parameterized import parameterized

from arbeitszeit.records import ProductionCosts
from arbeitszeit.transfers import TransferType
from arbeitszeit.use_cases import show_a_account_details
from arbeitszeit.use_cases.register_hours_worked import (
    RegisterHoursWorked,
    RegisterHoursWorkedRequest,
)
from tests.datetime_service import datetime_utc
from tests.use_cases.base_test_case import BaseTestCase


class UseCaseTester(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(
            show_a_account_details.ShowAAccountDetailsUseCase
        )
        self.register_hours_worked = self.injector.get(RegisterHoursWorked)

    def test_no_transfers_returned_when_no_transfers_took_place(self) -> None:
        self.member_generator.create_member()
        company = self.company_generator.create_company()
        response = self.use_case.show_details(self.create_use_case_request(company))
        assert not response.transfers

    def test_balance_is_zero_when_no_transfers_took_place(self) -> None:
        self.member_generator.create_member()
        company = self.company_generator.create_company()
        response = self.use_case.show_details(self.create_use_case_request(company))
        assert response.account_balance == 0

    def test_company_id_is_returned(self):
        self.member_generator.create_member()
        company = self.company_generator.create_company()
        response = self.use_case.show_details(self.create_use_case_request(company))
        assert response.company_id == company

    def test_that_no_info_is_generated_after_selling_of_consumer_product(self) -> None:
        company = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=company)
        response = self.use_case.show_details(self.create_use_case_request(company))
        transfers_before_consumption = len(response.transfers)
        self.consumption_generator.create_private_consumption(plan=plan)
        response = self.use_case.show_details(self.create_use_case_request(company))
        assert len(response.transfers) == transfers_before_consumption

    def test_that_no_info_is_generated_when_company_sells_p(self) -> None:
        company = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=company)
        response = self.use_case.show_details(self.create_use_case_request(company))
        transfers_before_consumption = len(response.transfers)
        self.consumption_generator.create_fixed_means_consumption(plan=plan)
        response = self.use_case.show_details(self.create_use_case_request(company))
        assert len(response.transfers) == transfers_before_consumption

    def test_after_approving_a_plan_one_transfer_is_recorded(self) -> None:
        company = self.company_generator.create_company()
        self.plan_generator.create_plan(planner=company)
        response = self.use_case.show_details(self.create_use_case_request(company))
        assert len(response.transfers) == 1

    def test_after_approving_a_plan_and_registering_work_two_transfers_are_recorded(
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
        response = self.use_case.show_details(self.create_use_case_request(company))
        assert len(response.transfers) == 2

    def test_two_transfers_are_recorded_in_descending_order(self) -> None:
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
        response = self.use_case.show_details(self.create_use_case_request(company))
        assert response.transfers[0].transfer_type == TransferType.work_certificates
        assert response.transfers[1].transfer_type == TransferType.credit_a

    @parameterized.expand(
        [
            (True, TransferType.credit_public_a),
            (False, TransferType.credit_a),
        ]
    )
    def test_that_correct_transfer_type_is_generated_when_credit_for_wages_is_granted(
        self,
        is_public_service: bool,
        expected_transfer_type: TransferType,
    ) -> None:
        company = self.company_generator.create_company()
        self.plan_generator.create_plan(
            planner=company,
            is_public_service=is_public_service,
        )
        response = self.use_case.show_details(self.create_use_case_request(company))
        assert response.transfers[0].transfer_type == expected_transfer_type

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
        response = self.use_case.show_details(self.create_use_case_request(company))
        assert len(response.transfers) == 1
        assert response.transfers[0].transfer_volume == Decimal(8.5)
        assert isinstance(response.transfers[0].date, datetime)
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
        response = self.use_case.show_details(self.create_use_case_request(company))
        transfer = response.transfers[0]
        assert transfer.transfer_type == TransferType.work_certificates
        assert transfer.transfer_volume == -hours_worked
        assert response.account_balance == -hours_worked

    def test_that_plotting_info_is_empty_when_no_transfers_occurred(self) -> None:
        self.member_generator.create_member()
        company = self.company_generator.create_company()
        response = self.use_case.show_details(self.create_use_case_request(company))
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
        response = self.use_case.show_details(self.create_use_case_request(own_company))
        assert response.plot.timestamps
        assert response.plot.accumulated_volumes

    def test_that_correct_plotting_info_is_generated_after_transferring_of_work_certs_to_two_workers(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime_utc(2000, 1, 1))
        worker1 = self.member_generator.create_member()
        worker2 = self.member_generator.create_member()
        own_company = self.company_generator.create_company(workers=[worker1, worker2])
        expected_transfer_1_timestamp = datetime_utc(2000, 1, 2)
        self.datetime_service.freeze_time(expected_transfer_1_timestamp)
        self.register_hours_worked(
            RegisterHoursWorkedRequest(
                company_id=own_company,
                worker_id=worker1,
                hours_worked=Decimal("10"),
            )
        )
        expected_transfer_2_timestamp = datetime_utc(2000, 1, 3)
        self.datetime_service.freeze_time(expected_transfer_2_timestamp)
        self.register_hours_worked(
            RegisterHoursWorkedRequest(
                company_id=own_company,
                worker_id=worker2,
                hours_worked=Decimal("10"),
            )
        )
        response = self.use_case.show_details(self.create_use_case_request(own_company))
        assert len(response.plot.timestamps) == 2
        assert len(response.plot.accumulated_volumes) == 2

        assert expected_transfer_1_timestamp in response.plot.timestamps
        assert expected_transfer_2_timestamp in response.plot.timestamps

        assert Decimal("-10") in response.plot.accumulated_volumes
        assert Decimal("-20") in response.plot.accumulated_volumes

    def test_that_plotting_info_is_generated_in_the_correct_order_after_transfer_of_certs_to_three_workers(
        self,
    ) -> None:
        worker1 = self.member_generator.create_member()
        worker2 = self.member_generator.create_member()
        worker3 = self.member_generator.create_member()
        own_company = self.company_generator.create_company(
            workers=[worker1, worker2, worker3]
        )

        first_transfer_timestamp = datetime_utc(2000, 1, 1)
        self.datetime_service.freeze_time(first_transfer_timestamp)
        self.register_hours_worked(
            RegisterHoursWorkedRequest(
                company_id=own_company,
                worker_id=worker1,
                hours_worked=Decimal("10"),
            )
        )
        second_transfer_timestamp = datetime_utc(2000, 1, 2)
        self.datetime_service.freeze_time(second_transfer_timestamp)
        self.register_hours_worked(
            RegisterHoursWorkedRequest(
                company_id=own_company,
                worker_id=worker2,
                hours_worked=Decimal("10"),
            )
        )
        third_transfer_timestamp = datetime_utc(2000, 1, 3)
        self.datetime_service.freeze_time(third_transfer_timestamp)
        self.register_hours_worked(
            RegisterHoursWorkedRequest(
                company_id=own_company,
                worker_id=worker3,
                hours_worked=Decimal("10"),
            )
        )

        response = self.use_case.show_details(self.create_use_case_request(own_company))
        assert response.plot.timestamps[0] == first_transfer_timestamp
        assert response.plot.timestamps[2] == third_transfer_timestamp

        assert response.plot.accumulated_volumes[0] == Decimal(-10)
        assert response.plot.accumulated_volumes[2] == Decimal(-30)

    def test_that_correct_plotting_info_is_generated_after_receiving_of_work_certificates_from_social_accounting(
        self,
    ) -> None:
        transfer_timestamp = datetime_utc(2030, 1, 1)
        expected_labour_time = Decimal(123)
        self.datetime_service.freeze_time(transfer_timestamp)
        company = self.company_generator.create_company()
        self.plan_generator.create_plan(
            planner=company,
            costs=ProductionCosts(
                labour_cost=expected_labour_time,
                means_cost=Decimal(0),
                resource_cost=Decimal(0),
            ),
        )
        response = self.use_case.show_details(self.create_use_case_request(company))

        assert response.plot.timestamps
        assert response.plot.accumulated_volumes

        assert len(response.plot.timestamps) == 1
        assert len(response.plot.accumulated_volumes) == 1

        assert transfer_timestamp in response.plot.timestamps
        assert expected_labour_time in response.plot.accumulated_volumes

    def create_use_case_request(
        self, company_id: UUID
    ) -> show_a_account_details.Request:
        return show_a_account_details.Request(company=company_id)
