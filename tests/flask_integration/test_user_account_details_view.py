from typing import Optional

from parameterized import parameterized

from arbeitszeit.injector import Binder, CallableProvider, Module
from tests.flask_integration.dependency_injection import FlaskConfiguration

from .base_test_case import LogInUser, ViewTestCase


class UserAccountDetailsViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/user/account"

    @parameterized.expand(
        [
            (LogInUser.member,),
            (LogInUser.company,),
            (LogInUser.accountant,),
        ]
    )
    def test_that_authenticated_users_can_access_the_view(
        self, user_type: Optional[LogInUser]
    ) -> None:
        self.assert_response_has_expected_code(
            url=self.url,
            method="GET",
            expected_code=200,
            login=user_type,
        )

    def test_that_unauthenticated_user_is_redirected(self) -> None:
        self.assert_response_has_expected_code(
            url=self.url,
            method="GET",
            expected_code=302,
            login=None,
        )

    @parameterized.expand(
        [
            (LogInUser.member,),
            (LogInUser.company,),
            (LogInUser.accountant,),
        ]
    )
    def test_that_response_contains_user_id(self, login: LogInUser) -> None:
        member = self.login_user(login)
        response = self.client.get(self.url)
        assert str(member) in response.text


class DateAndTimezoneTestsBase(ViewTestCase):
    @property
    def configured_timezone(self) -> str | None:
        raise NotImplementedError()

    def get_injection_modules(self) -> list[Module]:
        configured_timezone = self.configured_timezone

        class _Module(Module):
            def configure(self, binder: Binder) -> None:
                super().configure(binder)
                binder[FlaskConfiguration] = CallableProvider(
                    _Module.provide_flask_configuration
                )

            @staticmethod
            def provide_flask_configuration() -> FlaskConfiguration:
                configuration = FlaskConfiguration.default()
                configuration["DEFAULT_USER_TIMEZONE"] = configured_timezone
                return configuration

        modules = super().get_injection_modules()
        modules.append(_Module())
        return modules


class DateAndTimezoneTestsForTokyo(DateAndTimezoneTestsBase):
    @property
    def configured_timezone(self) -> str:
        return "Asia/Tokyo"

    def test_that_current_time_is_shown_with_configured_timezone_info(self) -> None:
        self.login_user(LogInUser.member)
        response = self.client.get("/user/account")
        "(JST)" in response.text


class DateAndTimezoneTestsForNonexistentTimezone(DateAndTimezoneTestsBase):
    @property
    def configured_timezone(self) -> str:
        return "Does/Not/Exist"

    def test_that_current_time_is_shown_as_utc_if_nonexistent_timezone_is_configured(
        self,
    ) -> None:
        self.login_user(LogInUser.member)
        response = self.client.get("/user/account")
        "(UTC)" in response.text
