from uuid import uuid4

from arbeitszeit.interactors import query_private_consumptions as interactor
from arbeitszeit_web.www.controllers.query_private_consumptions_controller import (
    InvalidRequest,
    QueryPrivateConsumptionsController,
)
from tests.www.base_test_case import BaseTestCase


class QueryPrivateConsumptionsControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(QueryPrivateConsumptionsController)

    def test_that_resulting_request_contains_currently_logged_in_member_id(
        self,
    ) -> None:
        expected_member_id = uuid4()
        self.session.login_member(expected_member_id)
        request = self.controller.process_request()
        assert isinstance(request, interactor.Request)
        assert request.member == expected_member_id

    def test_that_companies_receive_403_forbidden(self) -> None:
        self.session.login_company(uuid4())
        request = self.controller.process_request()
        assert isinstance(request, InvalidRequest)
        assert request.status_code == 403

    def test_that_accountants_receive_403_forbidden(
        self,
    ) -> None:
        self.session.login_accountant(uuid4())
        request = self.controller.process_request()
        assert isinstance(request, InvalidRequest)
        assert request.status_code == 403

    def test_that_anonymous_user_receives_401_unauthorized(
        self,
    ) -> None:
        self.session.logout()
        request = self.controller.process_request()
        assert isinstance(request, InvalidRequest)
        assert request.status_code == 401
