from arbeitszeit_web.www.controllers.list_registered_hours_worked_controller import (
    ListRegisteredHoursWorkedController,
)
from tests.www.base_test_case import BaseTestCase


class ListRegisteredHoursWorkedControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(ListRegisteredHoursWorkedController)

    def test_that_request_contains_current_company_id(self) -> None:
        company = self.company_generator.create_company()
        self.session.login_company(company=company)
        request = self.controller.create_request()
        assert request.company_id == company
