from arbeitszeit_flask.extensions import mail

from .flask import ViewTestCase


class AuthenticatedCompanyTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company, _, self.email = self.login_company()
        self.company = self.confirm_company(company=self.company, email=self.email)
        self.url = "/member/signup"

    def test_authenticated_company_gets_200_when_accessing_member_page(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_user_type_in_session_is_set_to_none_when_company_accesses_member_page(
        self,
    ) -> None:
        with self.client.session_transaction() as session:
            self.assertEqual(session["user_type"], "company")
        self.client.get(self.url)
        with self.client.session_transaction() as session:
            self.assertIsNone(session["user_type"])


class UnauthenticatedAndUnconfirmedMemberTests(ViewTestCase):
    def setUp(self):
        super().setUp()
        self.url = "/member/signup"

    def test_unauthenticated_and_unconfirmed_users_get_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

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
