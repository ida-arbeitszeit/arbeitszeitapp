from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4

from arbeitszeit import email_notifications
from arbeitszeit.use_cases.request_coordination_transfer import (
    RequestCoordinationTransferUseCase,
)
from tests.use_cases.base_test_case import BaseTestCase


class RequestCoordinationTransferTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(RequestCoordinationTransferUseCase)

    def test_requesting_transfer_fails_if_candidate_is_a_member(self) -> None:
        member = self.member_generator.create_member()
        response = self.use_case.request_transfer(
            self.get_use_case_request(candidate=member)
        )
        self.assertTrue(response.is_rejected)
        self.assertEqual(
            response.rejection_reason,
            RequestCoordinationTransferUseCase.Response.RejectionReason.candidate_is_not_a_company,
        )

    def test_requesting_transfer_fails_if_candidate_is_an_accountant(self) -> None:
        accountant = self.accountant_generator.create_accountant()
        response = self.use_case.request_transfer(
            self.get_use_case_request(candidate=accountant)
        )
        self.assertTrue(response.is_rejected)
        self.assertEqual(
            response.rejection_reason,
            RequestCoordinationTransferUseCase.Response.RejectionReason.candidate_is_not_a_company,
        )

    def test_requesting_transfer_fails_if_candidate_is_not_an_existing_company(
        self,
    ) -> None:
        response = self.use_case.request_transfer(
            self.get_use_case_request(candidate=uuid4())
        )
        self.assertTrue(response.is_rejected)
        self.assertEqual(
            response.rejection_reason,
            RequestCoordinationTransferUseCase.Response.RejectionReason.candidate_is_not_a_company,
        )

    def test_requesting_transfer_fails_if_requesting_tenure_does_not_exist(
        self,
    ) -> None:
        candidate = self.company_generator.create_company()
        response = self.use_case.request_transfer(
            self.get_use_case_request(requesting_tenure=uuid4(), candidate=candidate)
        )
        self.assertTrue(response.is_rejected)
        self.assertEqual(
            response.rejection_reason,
            RequestCoordinationTransferUseCase.Response.RejectionReason.requesting_tenure_not_found,
        )

    def test_requesting_transfer_fails_if_candidate_is_current_coordinator_of_requesting_tenure(
        self,
    ) -> None:
        candidate_and_coordinator = self.company_generator.create_company()
        coordination_tenure = (
            self.coordination_tenure_generator.create_coordination_tenure(
                coordinator=candidate_and_coordinator
            )
        )
        response = self.use_case.request_transfer(
            self.get_use_case_request(
                requesting_tenure=coordination_tenure,
                candidate=candidate_and_coordinator,
            )
        )
        self.assertTrue(response.is_rejected)
        self.assertEqual(
            response.rejection_reason,
            RequestCoordinationTransferUseCase.Response.RejectionReason.candidate_is_current_coordinator,
        )

    def test_requesting_transfer_fails_if_requesting_tenure_is_not_current_tenure(
        self,
    ) -> None:
        self.datetime_service.freeze_time(timestamp=datetime(2020, 5, 1))
        cooperation = self.cooperation_generator.create_cooperation()
        old_tenure = self.coordination_tenure_generator.create_coordination_tenure(
            cooperation=cooperation
        )
        self.datetime_service.advance_time(dt=timedelta(days=1))
        self.coordination_tenure_generator.create_coordination_tenure(
            cooperation=cooperation
        )

        response = self.use_case.request_transfer(
            request=self.get_use_case_request(requesting_tenure=old_tenure)
        )
        self.assertTrue(response.is_rejected)
        self.assertEqual(
            response.rejection_reason,
            RequestCoordinationTransferUseCase.Response.RejectionReason.requesting_tenure_is_not_current_tenure,
        )

    def test_requesting_transfer_fails_if_requesting_tenure_has_already_requested_a_transfer(
        self,
    ) -> None:
        cooperation = self.cooperation_generator.create_cooperation()
        current_tenure = self.coordination_tenure_generator.create_coordination_tenure(
            cooperation=cooperation
        )
        self.use_case.request_transfer(
            request=self.get_use_case_request(requesting_tenure=current_tenure)
        )
        response = self.use_case.request_transfer(
            request=self.get_use_case_request(requesting_tenure=current_tenure)
        )
        self.assertTrue(response.is_rejected)
        self.assertEqual(
            response.rejection_reason,
            RequestCoordinationTransferUseCase.Response.RejectionReason.requesting_tenure_has_pending_transfer_request,
        )

    def test_requesting_transfer_can_succeed(self) -> None:
        cooperation = self.cooperation_generator.create_cooperation()
        current_tenure = self.coordination_tenure_generator.create_coordination_tenure(
            cooperation=cooperation
        )
        response = self.use_case.request_transfer(
            request=self.get_use_case_request(requesting_tenure=current_tenure)
        )
        self.assertFalse(response.is_rejected)

    def test_that_a_notification_gets_sent_after_successfull_transfer_request(
        self,
    ) -> None:
        self.successfully_request_a_transfer()
        self.assertTrue(self.delivered_notifications())

    def test_that_delivered_notification_contains_candidate_name(self) -> None:
        expected_name = "Candidate For Coordination Coop."
        candidate = self.company_generator.create_company(name=expected_name)
        self.successfully_request_a_transfer(candidate=candidate)
        notification = self.get_latest_notification_delivered()
        self.assertEqual(notification.candidate_name, expected_name)

    def test_that_delivered_notification_contains_candidate_email(self) -> None:
        expected_mail = "candidate_for_coordination@coop.org"
        candidate = self.company_generator.create_company(email=expected_mail)
        self.successfully_request_a_transfer(candidate=candidate)
        notification = self.get_latest_notification_delivered()
        self.assertEqual(notification.candidate_email, expected_mail)

    def test_that_delivered_notification_contains_cooperation_name(self) -> None:
        expected_name = "Cooperation Coop."
        cooperation = self.cooperation_generator.create_cooperation(name=expected_name)
        self.successfully_request_a_transfer(cooperation=cooperation)
        notification = self.get_latest_notification_delivered()
        self.assertEqual(notification.cooperation_name, expected_name)

    def test_that_delivered_notification_contains_cooperation_id(self) -> None:
        expected_cooperation_id = self.cooperation_generator.create_cooperation()
        self.successfully_request_a_transfer(cooperation=expected_cooperation_id)
        notification = self.get_latest_notification_delivered()
        self.assertEqual(notification.cooperation_id, expected_cooperation_id)

    def get_use_case_request(
        self, requesting_tenure: Optional[UUID] = None, candidate: Optional[UUID] = None
    ) -> RequestCoordinationTransferUseCase.Request:
        if requesting_tenure is None:
            requesting_tenure = (
                self.coordination_tenure_generator.create_coordination_tenure()
            )
        if candidate is None:
            candidate = self.company_generator.create_company()
        return RequestCoordinationTransferUseCase.Request(
            requesting_coordination_tenure=requesting_tenure, candidate=candidate
        )

    def successfully_request_a_transfer(
        self, cooperation: Optional[UUID] = None, candidate: Optional[UUID] = None
    ) -> None:
        if cooperation is None:
            cooperation = self.cooperation_generator.create_cooperation()
        current_tenure = self.coordination_tenure_generator.create_coordination_tenure(
            cooperation=cooperation
        )
        response = self.use_case.request_transfer(
            request=self.get_use_case_request(
                requesting_tenure=current_tenure, candidate=candidate
            )
        )
        self.assertFalse(response.is_rejected)

    def get_latest_notification_delivered(
        self,
    ) -> email_notifications.CoordinationTransferRequest:
        notifications = self.delivered_notifications()
        assert notifications
        return notifications[-1]

    def delivered_notifications(
        self,
    ) -> list[email_notifications.CoordinationTransferRequest]:
        return [
            m
            for m in self.email_sender.get_messages_sent()
            if isinstance(m, email_notifications.CoordinationTransferRequest)
        ]
