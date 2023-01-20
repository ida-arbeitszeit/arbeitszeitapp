from datetime import datetime

from arbeitszeit.use_cases import (
    CancelCooperationSolicitation,
    CancelCooperationSolicitationRequest,
)

from .base_test_case import BaseTestCase


class UseCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(CancelCooperationSolicitation)

    def test_that_false_is_returned_when_requester_is_not_planner(self) -> None:
        plan = self.plan_generator.create_plan()
        company = self.company_generator.create_company_entity()
        response = self.use_case(
            CancelCooperationSolicitationRequest(company.id, plan.id)
        )
        assert response == False

    def test_that_false_is_returned_when_plan_has_no_pending_requests(self) -> None:
        company = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=company)
        response = self.use_case(CancelCooperationSolicitationRequest(company, plan.id))
        assert response == False

    def test_that_true_is_returned_when_coop_request_gets_canceled(self) -> None:
        coop = self.coop_generator.create_cooperation()
        company = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            planner=company, activation_date=datetime.min, requested_cooperation=coop
        )
        assert plan.requested_cooperation is not None
        response = self.use_case(CancelCooperationSolicitationRequest(company, plan.id))
        assert response == True
        assert plan.requested_cooperation is None
