from unittest import TestCase
from uuid import uuid4

from arbeitszeit_web.controllers.show_company_work_invite_details_controller import (
    ShowCompanyWorkInviteDetailsController,
)

from ..session import FakeSession
from .dependency_injection import get_dependency_injector


class ControllerTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.session = self.injector.get(FakeSession)
        self.controller = self.injector.get(ShowCompanyWorkInviteDetailsController)

    def test_when_user_is_not_logged_in_then_dont_generate_use_case_request(
        self,
    ) -> None:
        self.session.set_current_user_id(None)
        use_case_request = self.controller.create_use_case_request(invite_id=uuid4())
        self.assertIsNone(use_case_request)

    def test_when_user_is_logged_in_then_generate_use_case_request(self) -> None:
        self.session.set_current_user_id(uuid4())
        use_case_request = self.controller.create_use_case_request(invite_id=uuid4())
        self.assertIsNotNone(use_case_request)

    def test_that_session_user_id_is_part_of_created_use_case_request(self) -> None:
        expected_id = uuid4()
        self.session.set_current_user_id(expected_id)
        use_case_request = self.controller.create_use_case_request(invite_id=uuid4())
        assert use_case_request
        self.assertEqual(expected_id, use_case_request.member)

    def test_that_invite_id_is_passed_on_to_use_case_request(self) -> None:
        expected_id = uuid4()
        self.session.set_current_user_id(uuid4())
        use_case_request = self.controller.create_use_case_request(
            invite_id=expected_id
        )
        assert use_case_request
        self.assertEqual(expected_id, use_case_request.invite)
