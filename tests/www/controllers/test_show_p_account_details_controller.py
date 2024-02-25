from uuid import uuid4

from arbeitszeit_web.www.controllers.show_p_account_details_controller import (
    ShowPAccountDetailsController,
)
from tests.www.base_test_case import BaseTestCase


class ControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(ShowPAccountDetailsController)

    def test_company_id_is_returned_unchanged_as_use_case_request(
        self,
    ) -> None:
        expected_company = uuid4()
        use_case_request = self.controller.create_request(company=expected_company)
        assert use_case_request.company == expected_company
