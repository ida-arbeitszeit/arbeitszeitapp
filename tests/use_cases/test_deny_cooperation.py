from datetime import datetime, timedelta
from uuid import uuid4

from arbeitszeit.use_cases.deny_cooperation import (
    DenyCooperation,
    DenyCooperationRequest,
    DenyCooperationResponse,
)
from arbeitszeit.use_cases.request_cooperation import (
    RequestCooperation,
    RequestCooperationRequest,
)

from .base_test_case import BaseTestCase


class UseCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.deny_cooperation = self.injector.get(DenyCooperation)
        self.request_cooperation = self.injector.get(RequestCooperation)

    def test_error_is_raises_when_plan_does_not_exist(self) -> None:
        requester = self.company_generator.create_company()
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=requester
        )
        request = DenyCooperationRequest(
            requester_id=requester, plan_id=uuid4(), cooperation_id=cooperation
        )
        response = self.deny_cooperation(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == DenyCooperationResponse.RejectionReason.plan_not_found
        )

    def test_error_is_raised_when_cooperation_does_not_exist(self) -> None:
        requester = self.company_generator.create_company()
        plan = self.plan_generator.create_plan()
        request = DenyCooperationRequest(
            requester_id=requester, plan_id=plan, cooperation_id=uuid4()
        )
        response = self.deny_cooperation(request)
        assert response.is_rejected
        assert (
            response.rejection_reason == response.RejectionReason.cooperation_not_found
        )

    def test_error_is_raised_when_cooperation_was_not_requested(self) -> None:
        requester = self.company_generator.create_company()
        plan = self.plan_generator.create_plan()
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=requester
        )
        request = DenyCooperationRequest(
            requester_id=requester, plan_id=plan, cooperation_id=cooperation
        )
        response = self.deny_cooperation(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == response.RejectionReason.cooperation_was_not_requested
        )

    def test_error_is_raised_when_requester_is_not_coordinator_of_cooperation(
        self,
    ) -> None:
        requester = self.company_generator.create_company()
        coordinator = self.company_generator.create_company()
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=coordinator
        )
        plan = self.plan_generator.create_plan(requested_cooperation=cooperation)
        request = DenyCooperationRequest(
            requester_id=requester, plan_id=plan, cooperation_id=cooperation
        )
        response = self.deny_cooperation(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == response.RejectionReason.requester_is_not_coordinator
        )

    def test_possible_to_deny_cooperation(self) -> None:
        requester = self.company_generator.create_company()
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=requester
        )
        plan = self.plan_generator.create_plan(requested_cooperation=cooperation)
        request = DenyCooperationRequest(
            requester_id=requester, plan_id=plan, cooperation_id=cooperation
        )
        response = self.deny_cooperation(request)
        assert not response.is_rejected

    def test_possible_to_request_cooperation_again_after_cooperation_has_been_denied(
        self,
    ) -> None:
        requester = self.company_generator.create_company()
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=requester
        )
        plan = self.plan_generator.create_plan(requested_cooperation=cooperation)
        request = DenyCooperationRequest(
            requester_id=requester, plan_id=plan, cooperation_id=cooperation
        )
        self.deny_cooperation(request)
        request_request = RequestCooperationRequest(
            requester_id=requester, plan_id=plan, cooperation_id=cooperation
        )
        self.request_cooperation(request_request)

    def test_that_cooperation_for_inactive_plans_cannot_be_denied(self) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        requester = self.company_generator.create_company()
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=requester
        )
        plan = self.plan_generator.create_plan(
            requested_cooperation=cooperation, timeframe=1
        )
        self.datetime_service.advance_time(timedelta(days=2))
        request = DenyCooperationRequest(
            requester_id=requester, plan_id=plan, cooperation_id=cooperation
        )
        response = self.deny_cooperation(request)
        assert response.is_rejected
        assert response.rejection_reason == response.RejectionReason.plan_is_inactive
