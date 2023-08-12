from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases.accept_cooperation import (
    AcceptCooperation,
    AcceptCooperationRequest,
)
from arbeitszeit.use_cases.request_cooperation import (
    RequestCooperation,
    RequestCooperationRequest,
    RequestCooperationResponse,
)
from tests.data_generators import CompanyGenerator, CooperationGenerator, PlanGenerator
from tests.datetime_service import FakeDatetimeService

from .dependency_injection import get_dependency_injector


class RequestCooperationTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.request_cooperation = self.injector.get(RequestCooperation)
        self.accept_cooperation = self.injector.get(AcceptCooperation)
        self.coop_generator = self.injector.get(CooperationGenerator)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.requester = self.company_generator.create_company()
        self.datetime_service = self.injector.get(FakeDatetimeService)

    def test_error_is_raised_when_plan_does_not_exist(self) -> None:
        cooperation = self.coop_generator.create_cooperation()
        request = RequestCooperationRequest(
            requester_id=self.requester,
            plan_id=uuid4(),
            cooperation_id=cooperation.id,
        )
        response = self.request_cooperation(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == RequestCooperationResponse.RejectionReason.plan_not_found
        )

    def test_error_is_raised_when_cooperation_does_not_exist(self) -> None:
        plan = self.plan_generator.create_plan()
        request = RequestCooperationRequest(
            requester_id=self.requester, plan_id=plan.id, cooperation_id=uuid4()
        )
        response = self.request_cooperation(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == RequestCooperationResponse.RejectionReason.cooperation_not_found
        )

    def test_error_is_raised_when_plan_has_already_cooperation(self) -> None:
        cooperation1 = self.coop_generator.create_cooperation()
        cooperation2 = self.coop_generator.create_cooperation(
            name="name2", coordinator=self.requester
        )
        plan = self.plan_generator.create_plan(cooperation=cooperation1)
        request = RequestCooperationRequest(
            requester_id=self.requester,
            plan_id=plan.id,
            cooperation_id=cooperation2.id,
        )

        response = self.request_cooperation(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == RequestCooperationResponse.RejectionReason.plan_has_cooperation
        )

    def test_error_is_raised_when_plan_is_already_requesting_cooperation(self) -> None:
        requester = self.company_generator.create_company()
        cooperation1 = self.coop_generator.create_cooperation()
        plan = self.plan_generator.create_plan(
            requested_cooperation=cooperation1,
        )
        cooperation2 = self.coop_generator.create_cooperation(coordinator=requester)
        request = RequestCooperationRequest(
            requester_id=requester, plan_id=plan.id, cooperation_id=cooperation2.id
        )
        response = self.request_cooperation(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == response.RejectionReason.plan_is_already_requesting_cooperation
        )

    def test_error_is_raised_when_plan_is_public_plan(self) -> None:
        requester = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(is_public_service=True)
        cooperation = self.coop_generator.create_cooperation(coordinator=requester)
        request = RequestCooperationRequest(
            requester_id=requester, plan_id=plan.id, cooperation_id=cooperation.id
        )
        response = self.request_cooperation(request)
        assert response.is_rejected
        assert (
            response.rejection_reason == response.RejectionReason.plan_is_public_service
        )

    def test_error_is_raised_when_requester_is_not_planner(self) -> None:
        requester = self.company_generator.create_company()
        plan = self.plan_generator.create_plan()
        cooperation = self.coop_generator.create_cooperation(coordinator=requester)
        request = RequestCooperationRequest(
            requester_id=requester, plan_id=plan.id, cooperation_id=cooperation.id
        )
        response = self.request_cooperation(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == response.RejectionReason.requester_is_not_planner
        )

    def test_requesting_cooperation_is_successful(self) -> None:
        requester = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=requester)
        cooperation = self.coop_generator.create_cooperation(coordinator=requester)
        request = RequestCooperationRequest(
            requester_id=requester, plan_id=plan.id, cooperation_id=cooperation.id
        )
        response = self.request_cooperation(request)
        assert not response.is_rejected

    def test_successful_cooperation_request_returns_coordinator_data(self) -> None:
        requester = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=requester)
        cooperation = self.coop_generator.create_cooperation(coordinator=requester)
        request = RequestCooperationRequest(
            requester_id=requester, plan_id=plan.id, cooperation_id=cooperation.id
        )
        response = self.request_cooperation(request)
        assert response.coordinator_name
        assert response.coordinator_email

    def test_succesfully_requesting_cooperation_makes_it_possible_to_accept_cooperation(
        self,
    ) -> None:
        requester = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=requester)
        cooperation = self.coop_generator.create_cooperation(coordinator=requester)
        request = RequestCooperationRequest(
            requester_id=requester, plan_id=plan.id, cooperation_id=cooperation.id
        )
        self.request_cooperation(request)
        assert plan.requested_cooperation

        accept_cooperation_response = self.accept_cooperation(
            AcceptCooperationRequest(requester, plan.id, plan.requested_cooperation)
        )
        assert not accept_cooperation_response.is_rejected
