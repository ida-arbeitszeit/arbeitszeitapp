from uuid import uuid4

import pytest

from arbeitszeit_web.www.controllers.get_accountant_account_details_controller import (
    GetAccountantAccountDetailsController,
)
from tests.session import FakeSession

from .base_test_case import BaseTestCase


class GetAccountantAccountDetailsControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(GetAccountantAccountDetailsController)
        self.session = self.injector.get(FakeSession)

    def test_processing_authenticated_request_from_accountant_does_not_raise(
        self,
    ) -> None:
        self.session.login_accountant(uuid4())
        self.controller.parse_web_request()

    def test_processing_unauthenticated_request_does_raise(self) -> None:
        self.session.logout()
        with pytest.raises(Exception):
            self.controller.parse_web_request()

    def test_that_processing_request_from_member_does_raise(self) -> None:
        self.session.login_member(uuid4())
        with pytest.raises(Exception):
            self.controller.parse_web_request()

    def test_that_processing_request_from_company_does_raise(self) -> None:
        self.session.login_company(uuid4())
        with pytest.raises(Exception):
            self.controller.parse_web_request()

    def test_that_user_id_is_propagated_to_request(self) -> None:
        expected_user_id = uuid4()
        self.session.login_accountant(expected_user_id)
        request = self.controller.parse_web_request()
        assert request.user_id == expected_user_id
