from typing import Optional

from parameterized import parameterized

from arbeitszeit_flask.extensions import mail

from .flask import LogInUser, ViewTestCase


class UserAccessTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/signup-member"

    @parameterized.expand(
        [
            (LogInUser.accountant, 200),
            (None, 200),
            (LogInUser.company, 200),
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


class UserTypeChangesTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/signup-member"

    def test_user_type_in_session_is_set_to_none_when_company_accesses_page(
        self,
    ) -> None:
        self.login_company()
        with self.client.session_transaction() as session:
            self.assertEqual(session["user_type"], "company")
        self.client.get(self.url)
        with self.client.session_transaction() as session:
            self.assertIsNone(session["user_type"])

    def test_user_type_in_session_is_set_to_none_when_accountant_accesses_page(
        self,
    ) -> None:
        self.login_accountant()
        with self.client.session_transaction() as session:
            self.assertEqual(session["user_type"], "accountant")
        self.client.get(self.url)
        with self.client.session_transaction() as session:
            self.assertIsNone(session["user_type"])

    def test_user_type_in_session_does_not_change_when_member_accesses_page(
        self,
    ) -> None:
        self.login_member()
        with self.client.session_transaction() as session:
            self.assertEqual(session["user_type"], "member")
        self.client.get(self.url)
        with self.client.session_transaction() as session:
            self.assertEqual(session["user_type"], "member")


class UnauthenticatedAndUnconfirmedMemberTests(ViewTestCase):
    def setUp(self):
        super().setUp()
        self.url = "/signup-member"

    def test_correct_posting_is_possible_and_redirects_user(self):
        response = self.client.post(
            self.url,
            data=dict(email="test@cp.org", name="test name", password="test_password"),
        )
        self.assertEqual(response.status_code, 302)

    def test_correct_posting_makes_that_confirmations_mail_is_sent_to_member(self):
        member_email = "test2@cp.org"
        with mail.record_messages() as outbox:
            response = self.client.post(
                self.url,
                data=dict(
                    email=member_email, name="test name", password="test_password"
                ),
            )
            self.assertEqual(response.status_code, 302)
            assert len(outbox) == 1
            assert outbox[0].sender == "test_sender@cp.org"
            assert outbox[0].recipients[0] == member_email
