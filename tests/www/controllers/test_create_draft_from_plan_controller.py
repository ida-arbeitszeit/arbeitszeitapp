from uuid import uuid4

from arbeitszeit_web.www.controllers.create_draft_from_plan_controller import (
    CreateDraftFromPlanController,
)
from tests.www.base_test_case import BaseTestCase


# It is okay (for now) to run the tests only for authenticated
# companies since other users are not able to call to the controller
# under test. We don't have any specific code to handle those cases
# anyway.
class AuthenticatedCompanyTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(CreateDraftFromPlanController)
        self.company = uuid4()
        self.session.login_company(self.company)

    def test_that_provided_uuid_is_forwarded_to_interactor_request(self) -> None:
        expected_plan = uuid4()
        request = self.controller.create_interactor_request(plan=expected_plan)
        assert request.plan == expected_plan

    def test_that_currently_logged_in_company_is_forwared_to_interactor_request(
        self,
    ) -> None:
        request = self.controller.create_interactor_request(plan=uuid4())
        assert request.company == self.company
