from typing import Optional

from parameterized import parameterized

from .base_test_case import LogInUser, ViewTestCase


class AuthTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/member/resend"

    @parameterized.expand(
        [
            (LogInUser.accountant, 302),
            (None, 302),
            (LogInUser.company, 302),
            (LogInUser.member, 302),
        ]
    )
    def test_correct_status_codes_on_get_requests(
        self, login: Optional[LogInUser], expected_code: int
    ) -> None:
        self.assert_response_has_expected_code(
            url=self.url,
            method="get",
            login=login,
            expected_code=expected_code,
        )


class AuthenticatedButUnconfirmedMemberTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/member/resend"
        self.member = self.login_member(confirm_member=False)

    def test_authenticated_and_unconfirmed_users_get_redirected_and_mail_gets_send(
        self,
    ) -> None:
        response = self.client.get(self.url)
        with self.email_service().record_messages() as outbox:  # type: ignore
            response = self.client.get(
                self.url,
            )
            self.assertEqual(response.status_code, 302)
            assert len(outbox) == 1


class ConfirmedMemberTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/member/resend"
        self.member = self.login_member(confirm_member=True)

    def test_already_confirmed_member_gets_redirected_and_no_mail_gets_sent(
        self,
    ) -> None:
        response = self.client.get(self.url)
        with self.email_service().record_messages() as outbox:  # type: ignore
            response = self.client.get(
                self.url,
            )
            self.assertEqual(response.status_code, 302)
            assert len(outbox) == 0
