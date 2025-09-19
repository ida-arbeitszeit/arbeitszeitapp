from uuid import uuid4

from parameterized import parameterized

from arbeitszeit_web.www.controllers.invite_worker_to_company_controller import (
    InviteWorkerToCompanyController,
)
from tests.request import FakeRequest
from tests.www.base_test_case import BaseTestCase


class InviteWorkerToCompanyControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(InviteWorkerToCompanyController)
        self.company_id = uuid4()
        self.session.login_company(company=self.company_id)

    @parameterized.expand(
        [
            ("",),
            ("1",),
            ("123-456",),
        ]
    )
    def test_controller_raises_form_error_if_form_has_incorrectly_formed_worker_id(
        self, worker_id: str
    ) -> None:
        request = FakeRequest()
        request.set_form("worker_id", worker_id)
        with self.assertRaises(InviteWorkerToCompanyController.FormError):
            self.controller.import_request_data(request)

    def test_controller_returns_interactor_request_with_id_of_currently_logged_in_company(
        self,
    ) -> None:
        EXPECTED_COMPANY = self.company_id
        request = FakeRequest()
        request.set_form("worker_id", str(uuid4()))
        interactor_request = self.controller.import_request_data(request)
        assert interactor_request.company == EXPECTED_COMPANY

    def test_controller_returns_interactor_request_with_worker_id_from_form(
        self,
    ) -> None:
        EXPECTED_WORKER = uuid4()
        request = FakeRequest()
        request.set_form("worker_id", str(EXPECTED_WORKER))
        interactor_request = self.controller.import_request_data(request)
        assert interactor_request.worker == EXPECTED_WORKER
