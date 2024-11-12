from uuid import uuid4

from arbeitszeit_web.www.controllers.remove_worker_from_company_controller import (
    RemoveWorkerFromCompanyController,
)
from tests.request import FakeRequest
from tests.www.base_test_case import BaseTestCase


class RemoveWorkerFromCompanyControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = RemoveWorkerFromCompanyController()
        self.company = self.company_generator.create_company()
        self.session.login_company(company=self.company)

    def test_no_use_case_request_when_worker_is_missing_in_query_string(self) -> None:
        web_request = FakeRequest()
        request = self.controller.create_use_case_request(
            web_request=web_request, session=self.session
        )
        assert request is None

    def test_no_use_case_request_when_worker_is_not_a_uuid(self) -> None:
        web_request = FakeRequest()
        web_request.set_arg("worker", "not-a-uuid")
        request = self.controller.create_use_case_request(
            web_request=web_request, session=self.session
        )
        assert request is None

    def test_use_case_request(self) -> None:
        web_request = FakeRequest()
        web_request.set_arg("worker", str(uuid4()))
        request = self.controller.create_use_case_request(
            web_request=web_request, session=self.session
        )
        assert request

    def test_use_case_request_has_company_from_session(self) -> None:
        web_request = FakeRequest()
        web_request.set_arg("worker", str(uuid4()))
        request = self.controller.create_use_case_request(
            web_request=web_request, session=self.session
        )
        assert request
        assert request.company == self.company

    def test_use_case_request_has_worker_from_query_string(self) -> None:
        worker = uuid4()
        web_request = FakeRequest()
        web_request.set_arg("worker", str(worker))
        request = self.controller.create_use_case_request(
            web_request=web_request, session=self.session
        )
        assert request
        assert request.worker == worker
