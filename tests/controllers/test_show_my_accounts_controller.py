from unittest import TestCase
from uuid import uuid4

from arbeitszeit_web.controllers.show_my_accounts_controller import (
    ShowMyAccountsController,
)
from tests.flask_integration.session import FakeSession


class ControllerTests(TestCase):
    def test_when_company_exists_then_the_user_is_identified_in_use_case_request(
        self,
    ) -> None:
        session = FakeSession()
        controller = ShowMyAccountsController(session=session)
        expected_user_id = uuid4()
        session.set_current_user_id(expected_user_id)
        use_case_request = controller.create_request()
        assert use_case_request is not None
        self.assertEqual(use_case_request.current_user, expected_user_id)
