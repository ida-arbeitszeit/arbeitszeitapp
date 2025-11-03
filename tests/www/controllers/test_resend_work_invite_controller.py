from uuid import uuid4

from arbeitszeit_web.www.controllers.resend_work_invite_controller import (
    ResendWorkInviteController,
)
from tests.www.base_test_case import BaseTestCase


class TestResendWorkInviteController(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.controller = self.injector.get(ResendWorkInviteController)
        self.company = self.company_generator.create_company()

    def test_that_interactor_request_contains_company_id_from_session(self) -> None:
        self.session.login_company(company=self.company)
        self.request.set_form("worker_id", str(uuid4()))
        interactor_request = self.controller.create_interactor_request(
            request=self.request
        )
        assert interactor_request.company == self.company

    def test_that_interactor_request_contains_worker_id_from_request_form(self) -> None:
        self.session.login_company(company=self.company)
        worker_id = uuid4()
        self.request.set_form("worker_id", str(worker_id))
        interactor_request = self.controller.create_interactor_request(
            request=self.request
        )
        assert interactor_request.worker == worker_id
