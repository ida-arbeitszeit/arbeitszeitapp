from uuid import uuid4

from arbeitszeit_web.www.controllers.cancel_hours_worked_controller import (
    CancelHoursWorkedController,
)
from tests.www.base_test_case import BaseTestCase


class ControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(CancelHoursWorkedController)

    def test_that_requester_is_current_user(self) -> None:
        expected_requester = uuid4()
        self.session.login_company(expected_requester)
        use_case_request = self.controller.create_use_case_request(uuid4())
        assert use_case_request.requester == expected_requester

    def test_that_registration_id_is_forwarded_to_use_case_request(self) -> None:
        company_id = uuid4()
        self.session.login_company(company=company_id)
        expected_registration_id = uuid4()
        use_case_request = self.controller.create_use_case_request(
            registration_id=expected_registration_id
        )
        assert use_case_request.registration_id == expected_registration_id
