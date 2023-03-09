from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases.end_cooperation import (
    EndCooperation,
    EndCooperationRequest,
    EndCooperationResponse,
)
from tests.data_generators import CompanyGenerator, CooperationGenerator, PlanGenerator

from .dependency_injection import get_dependency_injector
from .repositories import CooperationRepository


class TestEndCooperation(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.end_cooperation = self.injector.get(EndCooperation)
        self.coop_generator = self.injector.get(CooperationGenerator)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.cooperation_repository = self.injector.get(CooperationRepository)
        self.requester = self.company_generator.create_company()

    def test_error_is_raised_when_plan_does_not_exist(self) -> None:
        cooperation = self.coop_generator.create_cooperation()
        request = EndCooperationRequest(
            requester_id=self.requester,
            plan_id=uuid4(),
            cooperation_id=cooperation.id,
        )
        response = self.end_cooperation(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == EndCooperationResponse.RejectionReason.plan_not_found
        )

    def test_error_is_raised_when_cooperation_does_not_exist(self) -> None:
        plan = self.plan_generator.create_plan()
        request = EndCooperationRequest(
            requester_id=self.requester, plan_id=plan.id, cooperation_id=uuid4()
        )
        response = self.end_cooperation(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == EndCooperationResponse.RejectionReason.cooperation_not_found
        )

    def test_error_is_raised_when_plan_has_no_cooperation(self) -> None:
        cooperation = self.coop_generator.create_cooperation()
        plan = self.plan_generator.create_plan(cooperation=None)
        request = EndCooperationRequest(
            requester_id=self.requester,
            plan_id=plan.id,
            cooperation_id=cooperation.id,
        )
        response = self.end_cooperation(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == EndCooperationResponse.RejectionReason.plan_has_no_cooperation
        )

    def test_error_is_raised_when_requester_is_neither_coordinator_nor_planner(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan(
            cooperation=self.coop_generator.create_cooperation()
        )
        cooperation = self.coop_generator.create_cooperation(plans=[plan])

        request = EndCooperationRequest(
            requester_id=self.requester,
            plan_id=plan.id,
            cooperation_id=cooperation.id,
        )
        response = self.end_cooperation(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == EndCooperationResponse.RejectionReason.requester_is_not_authorized
        )

    def test_ending_of_cooperation_is_successful_when_requester_is_planner(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan(planner=self.requester)
        cooperation = self.coop_generator.create_cooperation(plans=[plan])

        request = EndCooperationRequest(
            requester_id=self.requester,
            plan_id=plan.id,
            cooperation_id=cooperation.id,
        )
        response = self.end_cooperation(request)
        assert not response.is_rejected

    def test_ending_of_cooperation_is_successful_when_requester_is_coordinator(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        cooperation = self.coop_generator.create_cooperation(
            plans=[plan], coordinator=self.requester
        )

        request = EndCooperationRequest(
            requester_id=self.requester,
            plan_id=plan.id,
            cooperation_id=cooperation.id,
        )
        response = self.end_cooperation(request)
        assert not response.is_rejected

    def test_ending_of_cooperation_is_successful_and_plan_deleted_from_coop(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan(planner=self.requester)
        cooperation = self.coop_generator.create_cooperation(plans=[plan])
        assert plan.cooperation == cooperation.id

        request = EndCooperationRequest(
            requester_id=self.requester,
            plan_id=plan.id,
            cooperation_id=cooperation.id,
        )
        response = self.end_cooperation(request)
        assert not response.is_rejected
        assert plan.cooperation is None

    def test_ending_of_cooperation_is_successful_and_coop_deleted_from_plan(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan(planner=self.requester)
        cooperation = self.coop_generator.create_cooperation(plans=[plan])
        assert plan.cooperation == cooperation.id
        request = EndCooperationRequest(
            requester_id=self.requester,
            plan_id=plan.id,
            cooperation_id=cooperation.id,
        )
        response = self.end_cooperation(request)
        assert not response.is_rejected
        assert plan.cooperation is None
