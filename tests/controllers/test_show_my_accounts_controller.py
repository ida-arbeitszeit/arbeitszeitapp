from unittest import TestCase
from uuid import uuid4

from arbeitszeit_web.controllers.show_my_accounts_controller import (
    ShowMyAccountsController,
)
from tests.session import FakeSession

from .dependency_injection import get_dependency_injector


class ControllerTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.session = self.injector.get(FakeSession)
        self.controller = self.injector.get(ShowMyAccountsController)

    def test_when_company_exists_then_the_user_is_identified_in_use_case_request(
        self,
    ) -> None:
        expected_user_id = uuid4()
        self.session.login_company(expected_user_id)
        use_case_request = self.controller.create_request()
        assert use_case_request is not None
        self.assertEqual(use_case_request.current_user, expected_user_id)
