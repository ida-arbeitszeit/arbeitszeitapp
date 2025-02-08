from decimal import Decimal
from uuid import UUID, uuid4

from arbeitszeit.use_cases import get_member_account, list_registered_hours_worked
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
        self.list_registered_hours_use_case = self.injector.get(
            list_registered_hours_worked.ListRegisteredHoursWorkedUseCase
        )
        self.get_member_account_use_case = self.injector.get(
            get_member_account.GetMemberAccount
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
        assert len(registered_hours_response.registered_hours_worked) == 0

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
        assert len(registered_hours_response.registered_hours_worked) == 0

    def test_deletion_of_hours_worked_entry_succeeds(
        self,
    ) -> None:
        registered_hours_worked_record = (
            self.registered_hours_worked_generator.create_registered_hours_worked(
                company=self.company_id, member=self.worker_id, amount=Decimal(10)
            )
        )
        assert registered_hours_worked_record
        registered_hours_response_before_cancel = (
            self.list_registered_hours_use_case.list_registered_hours_worked(
                list_registered_hours_worked.Request(self.company_id)
            )
        )
        assert len(registered_hours_response_before_cancel.registered_hours_worked) == 1
        use_case_request = self.create_request(
            requester=self.company_id, registration_id=registered_hours_worked_record.id
        )
        use_case_response = self.use_case.cancel_hours_worked(use_case_request)
        assert use_case_response.delete_succeeded is True
        registered_hours_response_after_cancel = (
            self.list_registered_hours_use_case.list_registered_hours_worked(
                list_registered_hours_worked.Request(self.company_id)
            )
        )
        assert len(registered_hours_response_after_cancel.registered_hours_worked) == 0

        get_member_account_response = self.get_member_account_use_case(
            member_id=self.worker_id
        )
        latest_transaction = get_member_account_response.transactions[0]
        assert latest_transaction.purpose == "Cancellation of registered hours worked"
        assert latest_transaction.transaction_volume == Decimal(-10)

    def create_request(
        self, requester: UUID, registration_id: UUID
    ) -> CancelHoursWorkedUseCaseRequest:
        return CancelHoursWorkedUseCaseRequest(
            requester=requester,
            registration_id=registration_id,
        )
