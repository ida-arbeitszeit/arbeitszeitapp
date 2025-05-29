from unittest import TestCase
from uuid import UUID, uuid4

from arbeitszeit.use_cases import get_coop_summary
from arbeitszeit.use_cases.end_cooperation import (
    EndCooperation,
    EndCooperationRequest,
    EndCooperationResponse,
)
from tests.data_generators import CompanyGenerator, CooperationGenerator, PlanGenerator

from .dependency_injection import get_dependency_injector


class TestEndCooperation(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.end_cooperation = self.injector.get(EndCooperation)
        self.coop_generator = self.injector.get(CooperationGenerator)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.requester = self.company_generator.create_company()
        self.get_coop_summary_use_case = self.injector.get(
            get_coop_summary.GetCoopSummary
        )

    def test_error_is_raised_when_plan_does_not_exist(self) -> None:
        cooperation = self.coop_generator.create_cooperation()
        request = EndCooperationRequest(
            requester_id=self.requester,
            plan_id=uuid4(),
            cooperation_id=cooperation,
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
            requester_id=self.requester, plan_id=plan, cooperation_id=uuid4()
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
            plan_id=plan,
            cooperation_id=cooperation,
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
        plan = self.plan_generator.create_plan()
        cooperation = self.coop_generator.create_cooperation(plans=[plan])

        request = EndCooperationRequest(
            requester_id=self.requester,
            plan_id=plan,
            cooperation_id=cooperation,
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
            plan_id=plan,
            cooperation_id=cooperation,
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
            plan_id=plan,
            cooperation_id=cooperation,
        )
        response = self.end_cooperation(request)
        assert not response.is_rejected

    def test_ending_of_cooperation_is_successful_and_plan_deleted_from_coop(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan(planner=self.requester)
        cooperation = self.coop_generator.create_cooperation(plans=[plan])
        request = EndCooperationRequest(
            requester_id=self.requester,
            plan_id=plan,
            cooperation_id=cooperation,
        )
        response = self.end_cooperation(request)
        assert not response.is_rejected
        assert not self.is_plan_in_cooperation(plan, cooperation)

    def is_plan_in_cooperation(self, plan: UUID, cooperation: UUID) -> bool:
        requester = self.company_generator.create_company()
        request = get_coop_summary.GetCoopSummaryRequest(
            coop_id=cooperation,
            requester_id=requester,
        )
        response = self.get_coop_summary_use_case(request)
        assert response
        return any([plan == p.plan_id for p in response.plans])
