from uuid import uuid4

from arbeitszeit_web.www.controllers.show_r_account_details_controller import (
    ShowRAccountDetailsController,
)
from tests.www.base_test_case import BaseTestCase


class ControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(ShowRAccountDetailsController)

    def test_company_id_is_returned_unchanged_as_interactor_request(
        self,
    ) -> None:
        expected_company = uuid4()
        interactor_request = self.controller.create_request(company=expected_company)
        assert interactor_request.company == expected_company
