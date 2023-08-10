from uuid import uuid4

from arbeitszeit_web.www.controllers.show_my_accounts_controller import (
    ShowMyAccountsController,
)
from tests.www.base_test_case import BaseTestCase


class ControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(ShowMyAccountsController)

    def test_when_company_exists_then_the_user_is_identified_in_use_case_request(
        self,
    ) -> None:
        expected_user_id = uuid4()
        self.session.login_company(expected_user_id)
        use_case_request = self.controller.create_request()
        assert use_case_request is not None
        self.assertEqual(use_case_request.current_user, expected_user_id)
