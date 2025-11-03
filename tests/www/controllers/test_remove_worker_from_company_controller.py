from uuid import uuid4

from arbeitszeit_web.www.controllers.remove_worker_from_company_controller import (
    RemoveWorkerFromCompanyController,
)
from tests.request import FakeRequest
from tests.www.base_test_case import BaseTestCase


class RemoveWorkerFromCompanyControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(RemoveWorkerFromCompanyController)
        self.company = self.company_generator.create_company()
        self.session.login_company(company=self.company)

    def test_no_interactor_request_when_worker_is_missing_in_form(self) -> None:
        web_request = FakeRequest()
        request = self.controller.create_interactor_request(
            web_request=web_request, session=self.session
        )
        assert request is None

    def test_warning_when_worker_is_missing_in_form(self) -> None:
        web_request = FakeRequest()
        assert not self.notifier.warnings
        self.controller.create_interactor_request(
            web_request=web_request, session=self.session
        )
        assert self.notifier.warnings

    def test_no_interactor_request_when_worker_is_not_a_uuid(self) -> None:
        web_request = FakeRequest()
        web_request.set_form("worker", "not-a-uuid")
        request = self.controller.create_interactor_request(
            web_request=web_request, session=self.session
        )
        assert request is None

    def test_warning_when_worker_is_not_a_uuid(self) -> None:
        web_request = FakeRequest()
        web_request.set_form("worker", "not-a-uuid")
        assert not self.notifier.warnings
        self.controller.create_interactor_request(
            web_request=web_request, session=self.session
        )
        assert self.notifier.warnings

    def test_interactor_request_is_returned_when_worker_id_is_uuid(self) -> None:
        web_request = FakeRequest()
        web_request.set_form("worker", str(uuid4()))
        request = self.controller.create_interactor_request(
            web_request=web_request, session=self.session
        )
        assert request

    def test_interactor_request_has_company_from_session(self) -> None:
        web_request = FakeRequest()
        web_request.set_form("worker", str(uuid4()))
        request = self.controller.create_interactor_request(
            web_request=web_request, session=self.session
        )
        assert request
        assert request.company == self.company

    def test_interactor_request_has_worker_from_form(self) -> None:
        worker = uuid4()
        web_request = FakeRequest()
        web_request.set_form("worker", str(worker))
        request = self.controller.create_interactor_request(
            web_request=web_request, session=self.session
        )
        assert request
        assert request.worker == worker
