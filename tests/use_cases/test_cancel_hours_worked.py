from decimal import Decimal
from uuid import UUID, uuid4

from arbeitszeit.use_cases import list_registered_hours_worked, register_hours_worked
from arbeitszeit.use_cases.cancel_hours_worked import CancelHoursWorkedUseCase
from arbeitszeit.use_cases.cancel_hours_worked import (
    Request as CancelHoursWorkedUseCaseRequest,
)

from .base_test_case import BaseTestCase


class UseCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(CancelHoursWorkedUseCase)
        self.worker_id = self.member_generator.create_member()
        self.company_id = self.company_generator.create_company(
            workers=[self.worker_id]
        )
        self.nr_of_registrations_in_db = 10
        self.register_hours_worked_use_case = self.injector.get(
            register_hours_worked.RegisterHoursWorked
        )
        self.list_registered_hours_use_case = self.injector.get(
            list_registered_hours_worked.ListRegisteredHoursWorkedUseCase
        )

        for _ in range(self.nr_of_registrations_in_db):
            self.register_hours_worked(
                company_id=self.company_id, worker=self.worker_id, hours=Decimal(5)
            )

    def test_that_deleting_random_registration_id_with_random_company_is_noop(
        self,
    ) -> None:
        use_case_request = self.create_request(
            requester=uuid4(), registration_id=uuid4()
        )
        use_case_response = self.use_case.cancel_hours_worked(use_case_request)
        assert use_case_response.delete_succeeded is False
        registered_hours_response = (
            self.list_registered_hours_use_case.list_registered_hours_worked(
                list_registered_hours_worked.Request(self.company_id)
            )
        )
        assert (
            len(registered_hours_response.registered_hours_worked)
            == self.nr_of_registrations_in_db
        )

    def test_that_delete_attempt_when_requester_is_not_equal_to_company_that_registered_hours_worked_is_noop(
        self,
    ) -> None:
        use_case_request = self.create_request(
            requester=self.company_id, registration_id=uuid4()
        )
        use_case_response = self.use_case.cancel_hours_worked(use_case_request)
        assert use_case_response.delete_succeeded is False
        registered_hours_response = (
            self.list_registered_hours_use_case.list_registered_hours_worked(
                list_registered_hours_worked.Request(self.company_id)
            )
        )
        assert (
            len(registered_hours_response.registered_hours_worked)
            == self.nr_of_registrations_in_db
        )

    def test_deletion_of_hours_worked_entry_succeeds(
        self,
    ) -> None:
        registered_hours_response = (
            self.list_registered_hours_use_case.list_registered_hours_worked(
                list_registered_hours_worked.Request(self.company_id)
            )
        )
        entry_to_be_deleted = registered_hours_response.registered_hours_worked[0]
        use_case_request = self.create_request(
            requester=self.company_id, registration_id=entry_to_be_deleted.id
        )
        use_case_response = self.use_case.cancel_hours_worked(use_case_request)
        assert use_case_response.delete_succeeded is True
        registered_hours_after_deletion = (
            self.list_registered_hours_use_case.list_registered_hours_worked(
                list_registered_hours_worked.Request(self.company_id)
            )
        )
        assert (
            len(registered_hours_after_deletion.registered_hours_worked)
            == self.nr_of_registrations_in_db - 1
        )
        assert (
            entry_to_be_deleted
            not in registered_hours_after_deletion.registered_hours_worked
        )

    def create_request(
        self, requester: UUID, registration_id: UUID
    ) -> CancelHoursWorkedUseCaseRequest:
        return CancelHoursWorkedUseCaseRequest(
            requester=requester,
            registration_id=registration_id,
        )

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
