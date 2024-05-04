from parameterized import parameterized

from arbeitszeit.injector import Binder, CallableProvider, Module
from arbeitszeit_flask.extensions import mail
from tests.flask_integration.dependency_injection import FlaskConfiguration

from .flask import LogInUser, ViewTestCase

URL = "/user/request-email-change"
AUTHENTICATED_USER_LOGINS = [
    (LogInUser.member,),
    (LogInUser.unconfirmed_member,),
    (LogInUser.company,),
    (LogInUser.unconfirmed_company,),
    (LogInUser.accountant,),
]


class RequestEmailChangeViewTests(ViewTestCase):
    @parameterized.expand(AUTHENTICATED_USER_LOGINS)
    def test_that_authenticated_users_get_400_response_on_post_without_data(
        self, login: LogInUser
    ) -> None:
        self.assert_response_has_expected_code(
            url=URL,
            method="POST",
            expected_code=400,
            login=login,
        )

    def test_that_member_gets_redirected_when_posting_with_new_email_address(
        self,
    ) -> None:
        self.login_member()
        response = self.client.post(
            URL,
            data={
                "new_email": "new_email@test.test",
            },
        )
        assert response.status_code == 302

    def test_that_unauthenticated_users_get_redirect_response_on_post_without_data(
        self,
    ) -> None:
        self.assert_response_has_expected_code(
            url=URL,
            method="POST",
            expected_code=403,
            login=None,
        )

    @parameterized.expand(AUTHENTICATED_USER_LOGINS)
    def test_that_authenticated_users_get_a_200_response_with_get_request(
        self, login: LogInUser
    ) -> None:
        self.assert_response_has_expected_code(
            url=URL,
            method="GET",
            expected_code=200,
            login=login,
        )

    def test_that_unauthenticated_user_gets_redirect_with_get_requests(self) -> None:
        self.assert_response_has_expected_code(
            url=URL,
            method="GET",
            expected_code=302,
            login=None,
        )


class SentEmailTestCase(ViewTestCase):
    @property
    def expected_admin_mail(self) -> str | None:
        raise NotImplementedError()

    def get_injection_modules(self) -> list[Module]:
        expected_admin_mail = self.expected_admin_mail

        class _Module(Module):
            def configure(self, binder: Binder) -> None:
                super().configure(binder)
                binder[FlaskConfiguration] = CallableProvider(
                    _Module.provide_flask_configuration
                )

            @staticmethod
            def provide_flask_configuration() -> FlaskConfiguration:
                configuration = FlaskConfiguration.default()
                if expected_admin_mail is None:
                    configuration.pop("MAIL_ADMIN", None)
                else:
                    configuration["MAIL_ADMIN"] = expected_admin_mail
                return configuration

        modules = super().get_injection_modules()
        modules.append(_Module())
        return modules


class SentEmailTestsWithoutAdminMailInConfig(SentEmailTestCase):
    @property
    def expected_admin_mail(self) -> str | None:
        return None

    def test_that_two_emails_get_sent_when_posting_with_new_email_address(self) -> None:
        self.login_member()
        with mail.record_messages() as outbox:  # type: ignore[attr-defined]
            response = self.client.post(
                URL,
                data={
                    "new_email": "new_email@test.test",
                },
            )
            assert response.status_code == 302
            assert len(outbox) == 2

    def test_that_one_email_is_sent_to_old_and_one_to_new_email_address(self) -> None:
        old_email = "old_email@test.test"
        new_email = "new_email@test.test"
        self.login_member(email=old_email)
        with mail.record_messages() as outbox:  # type: ignore[attr-defined]
            response = self.client.post(
                URL,
                data={
                    "new_email": new_email,
                },
            )
            assert response.status_code == 302
            recipients = [recipient for mail in outbox for recipient in mail.recipients]
            assert len(recipients) == 2
            assert old_email in recipients
            assert new_email in recipients


class SentEmailTestsWithAdminMailInConfig(SentEmailTestCase):
    @property
    def expected_admin_mail(self) -> str | None:
        return "test_admin_mail@mail.org"

    def test_that_admin_email_address_appears_in_html_of_one_mail_but_not_in_both(
        self,
    ) -> None:
        self.login_member()
        with mail.record_messages() as outbox:  # type: ignore[attr-defined]
            response = self.client.post(
                URL,
                data={
                    "new_email": "new_email@test.test",
                },
            )
            assert response.status_code == 302
            assert len(outbox) == 2
            assert (self.expected_admin_mail in outbox[0].html) ^ (
                self.expected_admin_mail in outbox[1].html
            )
