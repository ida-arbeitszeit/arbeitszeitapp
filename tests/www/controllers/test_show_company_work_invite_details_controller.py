from uuid import uuid4

from arbeitszeit_web.www.controllers.show_company_work_invite_details_controller import (
    ShowCompanyWorkInviteDetailsController,
)
from tests.www.base_test_case import BaseTestCase


class ControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(ShowCompanyWorkInviteDetailsController)

    def test_when_user_is_not_logged_in_then_dont_generate_interactor_request(
        self,
    ) -> None:
        self.session.logout()
        interactor_request = self.controller.create_interactor_request(
            invite_id=uuid4()
        )
        self.assertIsNone(interactor_request)

    def test_when_user_is_logged_in_then_generate_interactor_request(self) -> None:
        self.session.login_company(company=uuid4())
        interactor_request = self.controller.create_interactor_request(
            invite_id=uuid4()
        )
        self.assertIsNotNone(interactor_request)

    def test_that_session_user_id_is_part_of_created_interactor_request(self) -> None:
        expected_id = uuid4()
        self.session.login_company(company=expected_id)
        interactor_request = self.controller.create_interactor_request(
            invite_id=uuid4()
        )
        assert interactor_request
        self.assertEqual(expected_id, interactor_request.member)

    def test_that_invite_id_is_passed_on_to_interactor_request(self) -> None:
        expected_id = uuid4()
        self.session.login_company(company=uuid4())
        interactor_request = self.controller.create_interactor_request(
            invite_id=expected_id
        )
        assert interactor_request
        self.assertEqual(expected_id, interactor_request.invite)
