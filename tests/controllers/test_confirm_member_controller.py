from datetime import datetime, timedelta

from arbeitszeit_web.www.controllers.confirm_member_controller import (
    ConfirmMemberController,
)
from tests.datetime_service import FakeDatetimeService
from tests.token import FakeTokenService

from .base_test_case import BaseTestCase


class ConfirmMemberControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(ConfirmMemberController)
        self.token_service = self.injector.get(FakeTokenService)
        self.datetime_service = self.injector.get(FakeDatetimeService)

    def test_that_invalid_token_yields_no_use_case_request(self) -> None:
        assert self.controller.process_request(token="testtoken 123") is None

    def test_supplying_proper_token_yields_a_proper_request(
        self,
    ) -> None:
        token = self.token_service.generate_token("test@test.test")
        request = self.controller.process_request(token=token)
        assert request

    def test_string_encoded_in_token_is_used_as_email_address_in_request(self) -> None:
        expected_email_address = "test@test.test"
        token = self.token_service.generate_token(expected_email_address)
        request = self.controller.process_request(token=token)
        assert request
        assert request.email_address == expected_email_address

    def test_that_no_request_is_yielded_if_token_is_1_day_and_one_minute_old(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        token = self.token_service.generate_token("test@test.test")
        self.datetime_service.advance_time(timedelta(days=1, minutes=1))
        request = self.controller.process_request(token=token)
        assert not request

    def test_that_a_proper_request_is_yielded_if_token_is_23_hours_and_59_minutes_old(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        token = self.token_service.generate_token("test@test.test")
        self.datetime_service.advance_time(timedelta(hours=23, minutes=59))
        request = self.controller.process_request(token=token)
        assert request
