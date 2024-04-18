from parameterized import parameterized

from arbeitszeit_flask.extensions import mail

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


class SentEmailTests(ViewTestCase):
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

    def test_that_admin_email_address_appears_in_html_of_one_mail_if_admin_email_address_is_configured(
        self,
    ) -> None:
        admin_email = self.client.application.config.get("MAIL_ADMIN")
        assert admin_email
        self.login_member()
        with mail.record_messages() as outbox:  # type: ignore[attr-defined]
            response = self.client.post(
                URL,
                data={
                    "new_email": "new_email@test.test",
                },
            )
            assert response.status_code == 302
            assert (admin_email in outbox[0].html) ^ (admin_email in outbox[1].html)

    def test_that_admin_email_address_appears_in_neither_email_if_admin_email_adress_is_none(
        self,
    ) -> None:
        admin_email = self.client.application.config.get("MAIL_ADMIN")
        self.client.application.config["MAIL_ADMIN"] = None
        self.login_member()
        with mail.record_messages() as outbox:  # type: ignore[attr-defined]
            response = self.client.post(
                URL,
                data={
                    "new_email": "new_email@test.test",
                },
            )
            assert response.status_code == 302
            assert admin_email not in outbox[0].html
            assert admin_email not in outbox[1].html
