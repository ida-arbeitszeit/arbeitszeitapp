from uuid import uuid4

from arbeitszeit_web.www.controllers.show_my_accounts_controller import (
    ShowCompanyAccountsController,
)
from tests.www.base_test_case import BaseTestCase


class ControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(ShowCompanyAccountsController)

    def test_company_id_is_returned_unchanged_as_use_case_request(
        self,
    ) -> None:
        expected_company_id = uuid4()
        use_case_request = self.controller.create_request(
            company_id=expected_company_id
        )
        assert use_case_request.company == expected_company_id
