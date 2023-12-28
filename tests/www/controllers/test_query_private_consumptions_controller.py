from uuid import uuid4

from arbeitszeit_web.www.controllers.query_private_consumptions_controller import (
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
        assert request
        assert request.member == expected_member_id

    def test_that_no_request_is_returned_if_user_is_logged_in_as_company(self) -> None:
        self.session.login_company(uuid4())
        request = self.controller.process_request()
        assert request is None

    def test_that_no_request_is_returned_if_user_is_logged_in_as_accountant(
        self,
    ) -> None:
        self.session.login_accountant(uuid4())
        request = self.controller.process_request()
        assert request is None
