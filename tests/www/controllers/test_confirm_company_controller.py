from datetime import datetime, timedelta

from arbeitszeit_web.www.controllers.confirm_company_controller import (
    ConfirmCompanyController,
)
from tests.www.base_test_case import BaseTestCase


class ConfirmCompanyControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(ConfirmCompanyController)

    def test_that_no_request_is_yielded_if_token_is_a_random_string(self) -> None:
        assert self.controller.process_request(token="random string 123") is None

    def test_that_a_request_is_yielded_if_proper_token_is_supplied(self) -> None:
        request = self.controller.process_request(
            token=self.token_service.generate_token("test string")
        )
        assert request

    def test_that_email_address_encoded_in_token_is_used_in_request(self) -> None:
        expected_email_address = "test@test.test"
        request = self.controller.process_request(
            token=self.token_service.generate_token(expected_email_address)
        )
        assert request
        assert request.email_address == expected_email_address

    def test_token_valid_after_23_hours_and_59_minutes(self) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        token = self.token_service.generate_token("bla")
        self.datetime_service.advance_time(timedelta(hours=23, minutes=59))
        request = self.controller.process_request(token=token)
        assert request

    def test_token_not_valid_after_1_day_and_1_minute(self) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        token = self.token_service.generate_token("bla")
        self.datetime_service.advance_time(timedelta(days=1, minutes=1))
        request = self.controller.process_request(token=token)
        assert not request
