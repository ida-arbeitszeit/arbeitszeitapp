from arbeitszeit_flask.extensions import mail

from .flask import ViewTestCase


class AuthenticatedMemberTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.member = self.login_member(confirm_member=True)
        self.url = "/company/signup"

    def test_authenticated_member_gets_200_when_accessing_company_page(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_user_type_in_session_is_set_to_none_when_member_accesses_company_page(
        self,
    ) -> None:
        with self.client.session_transaction() as session:
            self.assertEqual(session["user_type"], "member")
        self.client.get(self.url)
        with self.client.session_transaction() as session:
            self.assertIsNone(session["user_type"])


class UnauthenticatedAndUnconfirmedCompanyTests(ViewTestCase):
    def setUp(self):
        super().setUp()
        self.url = "/company/signup"

    def test_unauthenticated_and_unconfirmed_company_gets_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_correct_posting_is_possible_and_redirects_company(self):
        response = self.client.post(
            self.url,
            data=dict(email="test@cp.org", name="test name", password="test_password"),
        )
        self.assertEqual(response.status_code, 302)

    def test_correct_posting_makes_that_confirmations_mail_is_sent_to_company(self):
        company_email = "test2@cp.org"
        with mail.record_messages() as outbox:
            response = self.client.post(
                self.url,
                data=dict(
                    email=company_email, name="test name", password="test_password"
                ),
            )
            self.assertEqual(response.status_code, 302)
            assert len(outbox) == 1
            assert outbox[0].sender == "test_sender@cp.org"
            assert outbox[0].recipients[0] == company_email
