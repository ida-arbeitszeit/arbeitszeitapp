from uuid import uuid4

from arbeitszeit_web.www.controllers.revoke_plan_filing_controller import (
    RevokePlanFilingController,
)
from tests.www.base_test_case import BaseTestCase


class RevokePlanFilingControllerTest(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(RevokePlanFilingController)
        self.requester = uuid4()
        self.session.login_company(company=self.requester)

    def test_id_of_the_plan_to_revoke_gets_passed_to_response_object(self) -> None:
        expected_id = uuid4()
        interactor_request = self.controller.create_request(plan_id=expected_id)
        assert interactor_request.plan == expected_id

    def test_the_requester_id_gets_passed_to_response_object(self) -> None:
        interactor_request = self.controller.create_request(plan_id=uuid4())
        assert interactor_request.requester == self.requester
