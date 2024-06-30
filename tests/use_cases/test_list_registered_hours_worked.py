from datetime import datetime
from decimal import Decimal
from uuid import UUID

from parameterized import parameterized

from arbeitszeit.use_cases import list_registered_hours_worked, register_hours_worked
from tests.use_cases.base_test_case import BaseTestCase


class ListRegisteredHoursWorkedTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(
            list_registered_hours_worked.ListRegisteredHoursWorkedUseCase
        )
        self.register_hours_worked_use_case = self.injector.get(
            register_hours_worked.RegisterHoursWorked
        )

    @parameterized.expand(
        [
            (0,),
            (1,),
            (2,),
            (3,),
        ]
    )
    def test_response_registration_count_matches_actual_work_registrations(
        self,
        num_of_registrations: int,
    ) -> None:
        worker_id = self.member_generator.create_member()
        company_id = self.company_generator.create_company(workers=[worker_id])
        for _ in range(num_of_registrations):
            self.register_hours_worked(
                company_id=company_id, worker=worker_id, hours=Decimal(5)
            )
        request = list_registered_hours_worked.Request(company_id=company_id)
        response = self.use_case.list_registered_hours_worked(request)
        assert len(response.registered_hours_worked) == num_of_registrations

    @parameterized.expand(
        [
            (0,),
            (1,),
            (2,),
            (3,),
        ]
    )
    def test_response_registration_count_matches_actual_work_registrations_when_company_has_two_workers(
        self,
        num_of_registrations: int,
    ) -> None:
        worker_1_id = self.member_generator.create_member()
        worker_2_id = self.member_generator.create_member()
        company_id = self.company_generator.create_company(
            workers=[worker_1_id, worker_2_id]
        )
        for _ in range(num_of_registrations):
            self.register_hours_worked(
                company_id=company_id, worker=worker_1_id, hours=Decimal(5)
            )
        request = list_registered_hours_worked.Request(company_id=company_id)
        response = self.use_case.list_registered_hours_worked(request)
        assert len(response.registered_hours_worked) == num_of_registrations

    def test_that_registrations_in_response_are_ordered_descending_by_date(
        self,
    ) -> None:
        worker_id = self.member_generator.create_member()
        company_id = self.company_generator.create_company(workers=[worker_id])
        self.register_hours_worked(
            company_id=company_id, worker=worker_id, hours=Decimal(5)
        )
        self.register_hours_worked(
            company_id=company_id, worker=worker_id, hours=Decimal(5)
        )
        request = list_registered_hours_worked.Request(company_id=company_id)
        response = self.use_case.list_registered_hours_worked(request)
        assert (
            response.registered_hours_worked[0].registered_on
            > response.registered_hours_worked[1].registered_on
        )

    def test_that_response_contains_registered_hours_worked(self) -> None:
        EXPECTED_HOURS = Decimal(5)
        worker_id = self.member_generator.create_member()
        company_id = self.company_generator.create_company(workers=[worker_id])
        self.register_hours_worked(
            company_id=company_id, worker=worker_id, hours=EXPECTED_HOURS
        )
        request = list_registered_hours_worked.Request(company_id=company_id)
        response = self.use_case.list_registered_hours_worked(request)
        assert response.registered_hours_worked[0].hours == EXPECTED_HOURS

    def test_that_response_contains_id_of_worker(self) -> None:
        worker_id = self.member_generator.create_member()
        company_id = self.company_generator.create_company(workers=[worker_id])
        self.register_hours_worked(
            company_id=company_id, worker=worker_id, hours=Decimal(5)
        )
        request = list_registered_hours_worked.Request(company_id=company_id)
        response = self.use_case.list_registered_hours_worked(request)
        assert response.registered_hours_worked[0].worker_id == worker_id

    def test_that_response_contains_name_of_worker(self) -> None:
        EXPECTED_WORKER_NAME = "John Doe"
        worker_id = self.member_generator.create_member(name=EXPECTED_WORKER_NAME)
        company_id = self.company_generator.create_company(workers=[worker_id])
        self.register_hours_worked(
            company_id=company_id, worker=worker_id, hours=Decimal(5)
        )
        request = list_registered_hours_worked.Request(company_id=company_id)
        response = self.use_case.list_registered_hours_worked(request)
        assert response.registered_hours_worked[0].worker_name == EXPECTED_WORKER_NAME

    def test_response_includes_registration_timestamp(self) -> None:
        EXPECTED_DATE = datetime(2024, 5, 1)
        worker_id = self.member_generator.create_member()
        company_id = self.company_generator.create_company(workers=[worker_id])
        self.datetime_service.freeze_time(EXPECTED_DATE)
        self.register_hours_worked(
            company_id=company_id, worker=worker_id, hours=Decimal(5)
        )
        request = list_registered_hours_worked.Request(company_id=company_id)
        response = self.use_case.list_registered_hours_worked(request)
        assert response.registered_hours_worked[0].registered_on == EXPECTED_DATE

    def register_hours_worked(
        self, company_id: UUID, worker: UUID, hours: Decimal
    ) -> None:
        request = register_hours_worked.RegisterHoursWorkedRequest(
            company_id=company_id,
            worker_id=worker,
            hours_worked=hours,
        )
        response = self.register_hours_worked_use_case(use_case_request=request)
        assert not response.is_rejected
