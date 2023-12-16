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

    def test_requesting_transfer_fails_if_requster_is_not_coordinator(
        self,
    ) -> None:
        cooperation = self.cooperation_generator.create_cooperation()
        response = self.use_case.request_transfer(
            self.get_use_case_request(cooperation=cooperation)
        )
        self.assertTrue(response.is_rejected)
        self.assertEqual(
            response.rejection_reason,
            RequestCoordinationTransferUseCase.Response.RejectionReason.requester_is_not_coordinator,
        )

    def test_requesting_transfer_fails_if_candidate_is_current_coordinator_of_cooperation(
        self,
    ) -> None:
        candidate_and_coordinator = self.company_generator.create_company()
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=candidate_and_coordinator
        )
        response = self.use_case.request_transfer(
            RequestCoordinationTransferUseCase.Request(
                requester=candidate_and_coordinator,
                candidate=candidate_and_coordinator,
                cooperation=cooperation,
            )
        )
        self.assertTrue(response.is_rejected)
        self.assertEqual(
            response.rejection_reason,
            RequestCoordinationTransferUseCase.Response.RejectionReason.candidate_is_current_coordinator,
        )

    def test_requesting_transfer_fails_if_current_coordinator_has_already_requested_a_transfer_that_is_still_pending(
        self,
    ) -> None:
        coordinator = self.company_generator.create_company()
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=coordinator
        )
        self.use_case.request_transfer(
            RequestCoordinationTransferUseCase.Request(
                requester=coordinator,
                candidate=self.company_generator.create_company(),
                cooperation=cooperation,
            )
        )
        response = self.use_case.request_transfer(
            RequestCoordinationTransferUseCase.Request(
                requester=coordinator,
                candidate=self.company_generator.create_company(),
                cooperation=cooperation,
            )
        )
        self.assertTrue(response.is_rejected)
        self.assertEqual(
            response.rejection_reason,
            RequestCoordinationTransferUseCase.Response.RejectionReason.coordination_tenure_has_pending_transfer_request,
        )

    def test_requesting_transfer_fails_if_cooperation_does_not_exist(self) -> None:
        response = self.use_case.request_transfer(
            self.get_use_case_request(cooperation=uuid4())
        )
        self.assertTrue(response.is_rejected)
        self.assertEqual(
            response.rejection_reason,
            RequestCoordinationTransferUseCase.Response.RejectionReason.cooperation_not_found,
        )

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
        coordinator = self.company_generator.create_company()
        cooperation = self.cooperation_generator.create_cooperation(
            name=expected_name, coordinator=coordinator
        )
        self.successfully_request_a_transfer(
            current_user=coordinator, cooperation=cooperation
        )
        notification = self.get_latest_notification_delivered()
        self.assertEqual(notification.cooperation_name, expected_name)

    def get_use_case_request(
        self,
        requester: Optional[UUID] = None,
        cooperation: Optional[UUID] = None,
        candidate: Optional[UUID] = None,
    ) -> RequestCoordinationTransferUseCase.Request:
        if requester is None:
            requester = self.company_generator.create_company()
        if cooperation is None:
            cooperation = self.cooperation_generator.create_cooperation()
        if candidate is None:
            candidate = self.company_generator.create_company()
        return RequestCoordinationTransferUseCase.Request(
            requester=requester, cooperation=cooperation, candidate=candidate
        )

    def successfully_request_a_transfer(
        self,
        current_user: Optional[UUID] = None,
        cooperation: Optional[UUID] = None,
        candidate: Optional[UUID] = None,
    ) -> None:
        if current_user is None:
            current_user = self.company_generator.create_company()
        if cooperation is None:
            cooperation = self.cooperation_generator.create_cooperation(
                coordinator=current_user
            )
        response = self.use_case.request_transfer(
            request=self.get_use_case_request(
                requester=current_user, cooperation=cooperation, candidate=candidate
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
