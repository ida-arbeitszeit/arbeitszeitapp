from datetime import UTC, datetime

from parameterized import parameterized

from arbeitszeit_flask.datetime import FlaskDatetimeFormatter, RealtimeDatetimeService
from tests.datetime_service import datetime_utc
from tests.flask_integration.flask import FlaskTestCase


class DatetimeTests(FlaskTestCase):
    def setUp(self):
        super().setUp()
        self.real_datetime_service = RealtimeDatetimeService()

    def test_that_now_returns_utc_datetime(self) -> None:
        now = self.real_datetime_service.now()
        assert now.tzinfo == UTC


class FormatterTests(FlaskTestCase):
    def setUp(self):
        super().setUp()
        self.datetime_formatter = FlaskDatetimeFormatter()

    def test_that_datetime_is_formatted_to_german_style_by_default(self) -> None:
        original_datetime = datetime_utc(2025, 5, 2, 10, 30, 10)
        formatted_datetime = self.datetime_formatter.format_datetime(
            date=original_datetime
        )
        assert formatted_datetime == "02.05.2025 10:30"

    def test_that_format_can_be_customized(self) -> None:
        original_datetime = datetime_utc(2025, 5, 2)
        formatted_datetime = self.datetime_formatter.format_datetime(
            date=original_datetime,
            fmt="%d.%m.",
        )
        assert formatted_datetime == "02.05."

    def test_that_datetime_has_a_timezone_after_formatting(self) -> None:
        timezone_offset_string = self.datetime_formatter.format_datetime(
            date=datetime.now(tz=None), fmt="%z"
        )
        assert timezone_offset_string

    @parameterized.expand([("GMT"), ("EST")])
    def test_that_datetime_is_formatted_as_valid_user_timezone_from_app_config(
        self, valid_user_timezone_name: str
    ) -> None:
        self.app.config["DEFAULT_USER_TIMEZONE"] = valid_user_timezone_name
        formatted_datetime = self.datetime_formatter.format_datetime(
            date=datetime.now(), fmt="%Z"
        )
        assert formatted_datetime == valid_user_timezone_name

    def test_that_datetime_is_formatted_as_UTC_if_app_config_has_invalid_user_timezone(
        self,
    ) -> None:
        self.app.config["DEFAULT_USER_TIMEZONE"] = "INVALID_TIMEZONE"
        formatted_datetime = self.datetime_formatter.format_datetime(
            date=datetime.now(), fmt="%Z"
        )
        assert formatted_datetime == "UTC"
