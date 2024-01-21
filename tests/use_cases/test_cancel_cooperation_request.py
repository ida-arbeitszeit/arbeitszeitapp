from uuid import UUID

from arbeitszeit.use_cases import list_outbound_coop_requests
from arbeitszeit.use_cases.cancel_cooperation_solicitation import (
    CancelCooperationSolicitation,
    CancelCooperationSolicitationRequest,
)

from .base_test_case import BaseTestCase


class UseCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(CancelCooperationSolicitation)
        self.list_outbound_coop_requests_use_case = self.injector.get(
            list_outbound_coop_requests.ListOutboundCoopRequests
        )

    def test_that_false_is_returned_when_requester_is_not_planner(self) -> None:
        plan = self.plan_generator.create_plan()
        company = self.company_generator.create_company_record()
        response = self.use_case(
            CancelCooperationSolicitationRequest(company.id, plan.id)
        )
        assert not response

    def test_that_false_is_returned_when_plan_has_no_pending_requests(self) -> None:
        company = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=company)
        response = self.use_case(CancelCooperationSolicitationRequest(company, plan.id))
        assert not response

    def test_that_plan_is_not_requesting_cooperation_after_cancelation_was_requested(
        self,
    ) -> None:
        coop = self.cooperation_generator.create_cooperation()
        company = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            planner=company, requested_cooperation=coop
        )
        self.use_case(CancelCooperationSolicitationRequest(company, plan.id))
        assert not self._is_plan_requesting_cooperation(plan=plan.id, planner=company)

    def test_that_true_is_returned_when_coop_request_gets_canceled(self) -> None:
        coop = self.cooperation_generator.create_cooperation()
        company = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            planner=company, requested_cooperation=coop
        )
        response = self.use_case(CancelCooperationSolicitationRequest(company, plan.id))
        assert response

    def _is_plan_requesting_cooperation(self, plan: UUID, planner: UUID) -> bool:
        response = self.list_outbound_coop_requests_use_case(
            list_outbound_coop_requests.ListOutboundCoopRequestsRequest(
                requester_id=planner
            )
        )
        return any(
            plan == coop_request.plan_id
            for coop_request in response.cooperation_requests
        )
