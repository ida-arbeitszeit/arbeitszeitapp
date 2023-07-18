from uuid import uuid4

import pytest

from arbeitszeit_web.www.controllers.get_company_account_details_controller import (
    GetCompanyAccountDetailsController,
)
from tests.session import FakeSession

from .base_test_case import BaseTestCase


class GetCompanyAccountDetailsControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.session = self.injector.get(FakeSession)
        self.controller = self.injector.get(GetCompanyAccountDetailsController)

    def test_that_exception_is_raised_when_user_is_not_logged_in(self) -> None:
        self.session.logout()
        with pytest.raises(Exception):
            self.controller.parse_web_request()

    def test_that_no_exception_is_raised_when_user_is_logged_in_as_company(
        self,
    ) -> None:
        self.session.login_company(uuid4())
        self.controller.parse_web_request()

    def test_an_exception_is_raised_when_user_is_logged_in_as_member(self) -> None:
        self.session.login_member(uuid4())
        with pytest.raises(Exception):
            self.controller.parse_web_request()

    def test_resulting_request_contains_id_of_current_user(
        self,
    ) -> None:
        expected_user_id = uuid4()
        self.session.login_company(expected_user_id)
        request = self.controller.parse_web_request()
        assert request.user_id == expected_user_id
