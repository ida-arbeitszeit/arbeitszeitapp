from uuid import uuid4

from parameterized import parameterized

from arbeitszeit import email_notifications
from arbeitszeit.interactors.accept_cooperation import (
    AcceptCooperationInteractor,
    AcceptCooperationRequest,
)
from arbeitszeit.interactors.request_cooperation import (
    RequestCooperationInteractor,
    RequestCooperationRequest,
    RequestCooperationResponse,
)

from .base_test_case import BaseTestCase


class RequestCooperationTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(RequestCooperationInteractor)
        self.accept_cooperation = self.injector.get(AcceptCooperationInteractor)
        self.requester = self.company_generator.create_company()

    def test_error_is_raised_when_plan_does_not_exist(self) -> None:
        cooperation = self.cooperation_generator.create_cooperation()
        request = RequestCooperationRequest(
            requester_id=self.requester,
            plan_id=uuid4(),
            cooperation_id=cooperation,
        )
        response = self.interactor.execute(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == RequestCooperationResponse.RejectionReason.plan_not_found
        )

    def test_error_is_raised_when_cooperation_does_not_exist(self) -> None:
        plan = self.plan_generator.create_plan()
        request = RequestCooperationRequest(
            requester_id=self.requester, plan_id=plan, cooperation_id=uuid4()
        )
        response = self.interactor.execute(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == RequestCooperationResponse.RejectionReason.cooperation_not_found
        )

    def test_error_is_raised_when_plan_has_already_cooperation(self) -> None:
        cooperation1 = self.cooperation_generator.create_cooperation()
        cooperation2 = self.cooperation_generator.create_cooperation(
            name="name2", coordinator=self.requester
        )
        plan = self.plan_generator.create_plan(cooperation=cooperation1)
        request = RequestCooperationRequest(
            requester_id=self.requester,
            plan_id=plan,
            cooperation_id=cooperation2,
        )

        response = self.interactor.execute(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == RequestCooperationResponse.RejectionReason.plan_has_cooperation
        )

    def test_error_is_raised_when_plan_is_already_requesting_cooperation(self) -> None:
        requester = self.company_generator.create_company()
        cooperation1 = self.cooperation_generator.create_cooperation()
        plan = self.plan_generator.create_plan(
            requested_cooperation=cooperation1,
        )
        cooperation2 = self.cooperation_generator.create_cooperation(
            coordinator=requester
        )
        request = RequestCooperationRequest(
            requester_id=requester, plan_id=plan, cooperation_id=cooperation2
        )
        response = self.interactor.execute(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == response.RejectionReason.plan_is_already_requesting_cooperation
        )

    def test_error_is_raised_when_plan_is_public_plan(self) -> None:
        requester = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(is_public_service=True)
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=requester
        )
        request = RequestCooperationRequest(
            requester_id=requester, plan_id=plan, cooperation_id=cooperation
        )
        response = self.interactor.execute(request)
        assert response.is_rejected
        assert (
            response.rejection_reason == response.RejectionReason.plan_is_public_service
        )

    def test_error_is_raised_when_requester_is_not_planner(self) -> None:
        requester = self.company_generator.create_company()
        plan = self.plan_generator.create_plan()
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=requester
        )
        request = RequestCooperationRequest(
            requester_id=requester, plan_id=plan, cooperation_id=cooperation
        )
        response = self.interactor.execute(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == response.RejectionReason.requester_is_not_planner
        )

    def test_requesting_cooperation_is_successful(self) -> None:
        requester = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=requester)
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=requester
        )
        request = RequestCooperationRequest(
            requester_id=requester, plan_id=plan, cooperation_id=cooperation
        )
        response = self.interactor.execute(request)
        assert not response.is_rejected

    def test_successful_cooperation_request_returns_coordinator_data(self) -> None:
        requester = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=requester)
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=requester
        )
        request = RequestCooperationRequest(
            requester_id=requester, plan_id=plan, cooperation_id=cooperation
        )
        response = self.interactor.execute(request)
        assert response.coordinator_name
        assert response.coordinator_email

    def test_succesfully_requesting_cooperation_makes_it_possible_to_accept_cooperation(
        self,
    ) -> None:
        requester = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=requester)
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=requester
        )
        request = RequestCooperationRequest(
            requester_id=requester, plan_id=plan, cooperation_id=cooperation
        )
        self.interactor.execute(request)
        accept_cooperation_response = self.accept_cooperation.execute(
            AcceptCooperationRequest(requester, plan, cooperation)
        )
        assert not accept_cooperation_response.is_rejected

    def test_that_after_requesting_successfully_an_email_was_sent_out(self) -> None:
        requester = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=requester)
        cooperation = self.cooperation_generator.create_cooperation()
        request = RequestCooperationRequest(
            requester_id=requester, plan_id=plan, cooperation_id=cooperation
        )
        messages_before_request = len(self.email_sender.get_messages_sent())
        response = self.interactor.execute(request)
        assert not response.is_rejected
        assert len(self.email_sender.get_messages_sent()) == messages_before_request + 1

    def test_that_after_requesting_successfully_a_cooperation_request_email_was_sent(
        self,
    ) -> None:
        requester = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=requester)
        cooperation = self.cooperation_generator.create_cooperation()
        request = RequestCooperationRequest(
            requester_id=requester, plan_id=plan, cooperation_id=cooperation
        )
        messages_before_request = len(self.get_cooperation_request_emails())
        response = self.interactor.execute(request)
        assert not response.is_rejected
        assert len(self.get_cooperation_request_emails()) == messages_before_request + 1

    @parameterized.expand(
        [
            ("test@test.test",),
            ("other@test.test",),
        ]
    )
    def test_that_after_requesting_successfully_the_email_sent_contains_the_expected_coordinator_email_address(
        self, expected_email_address: str
    ) -> None:
        requester = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=requester)
        coordinator = self.company_generator.create_company(
            email=expected_email_address
        )
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=coordinator
        )
        request = RequestCooperationRequest(
            requester_id=requester, plan_id=plan, cooperation_id=cooperation
        )
        response = self.interactor.execute(request)
        assert not response.is_rejected
        assert (
            self.get_latest_cooperation_request_email().coordinator_email_address
            == expected_email_address
        )

    @parameterized.expand(
        [
            ("test name",),
            ("other name",),
        ]
    )
    def test_that_after_requesting_successfully_the_email_sent_contains_the_expected_coordinator_name(
        self, expected_name: str
    ) -> None:
        requester = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=requester)
        coordinator = self.company_generator.create_company(name=expected_name)
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=coordinator
        )
        request = RequestCooperationRequest(
            requester_id=requester, plan_id=plan, cooperation_id=cooperation
        )
        response = self.interactor.execute(request)
        assert not response.is_rejected
        assert (
            self.get_latest_cooperation_request_email().coordinator_name
            == expected_name
        )

    def get_latest_cooperation_request_email(
        self,
    ) -> email_notifications.CooperationRequestEmail:
        emails = self.get_cooperation_request_emails()
        assert emails
        return emails[-1]

    def get_cooperation_request_emails(
        self,
    ) -> list[email_notifications.CooperationRequestEmail]:
        return [
            m
            for m in self.email_sender.get_messages_sent()
            if isinstance(m, email_notifications.CooperationRequestEmail)
        ]
