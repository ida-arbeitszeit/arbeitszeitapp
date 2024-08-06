from uuid import UUID

from arbeitszeit.use_cases import show_company_cooperations
from arbeitszeit.use_cases.cancel_cooperation_solicitation import (
    CancelCooperationSolicitation,
    CancelCooperationSolicitationRequest,
)

from .base_test_case import BaseTestCase


class UseCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(CancelCooperationSolicitation)
        self.show_company_cooperations = self.injector.get(
            show_company_cooperations.ShowCompanyCooperationsUseCase
        )

    def test_that_false_is_returned_when_requester_is_not_planner(self) -> None:
        plan = self.plan_generator.create_plan()
        company = self.company_generator.create_company_record()
        response = self.use_case(CancelCooperationSolicitationRequest(company.id, plan))
        assert not response

    def test_that_false_is_returned_when_plan_has_no_pending_requests(self) -> None:
        company = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=company)
        response = self.use_case(CancelCooperationSolicitationRequest(company, plan))
        assert not response

    def test_that_plan_is_not_requesting_cooperation_after_cancelation_was_requested(
        self,
    ) -> None:
        coop = self.cooperation_generator.create_cooperation()
        company = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            planner=company, requested_cooperation=coop
        )
        self.use_case(CancelCooperationSolicitationRequest(company, plan))
        assert not self._is_plan_requesting_cooperation(plan=plan, planner=company)

    def test_that_true_is_returned_when_coop_request_gets_canceled(self) -> None:
        coop = self.cooperation_generator.create_cooperation()
        company = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            planner=company, requested_cooperation=coop
        )
        response = self.use_case(CancelCooperationSolicitationRequest(company, plan))
        assert response

    def _is_plan_requesting_cooperation(self, plan: UUID, planner: UUID) -> bool:
        response = self.show_company_cooperations.show_company_cooperations(
            show_company_cooperations.Request(company=planner)
        )
        return any(
            plan == coop_request.plan_id
            for coop_request in response.outbound_cooperation_requests
        )
